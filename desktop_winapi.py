import ctypes
from ctypes import wintypes


user32 = ctypes.WinDLL("user32", use_last_error=True)

LONG_PTR = ctypes.c_longlong if ctypes.sizeof(ctypes.c_void_p) == 8 else ctypes.c_long
ULONG_PTR = ctypes.c_ulonglong if ctypes.sizeof(ctypes.c_void_p) == 8 else ctypes.c_ulong

GWL_EXSTYLE = -20
SMTO_NORMAL = 0x0000
SWP_NOMOVE = 0x0002
SWP_NOSIZE = 0x0001
SWP_NOACTIVATE = 0x0010
SWP_FRAMECHANGED = 0x0020
SW_SHOW = 5
HWND_BOTTOM = 1
WS_EX_APPWINDOW = 0x00040000
WS_EX_TOOLWINDOW = 0x00000080


EnumWindowsProc = ctypes.WINFUNCTYPE(wintypes.BOOL, wintypes.HWND, wintypes.LPARAM)

user32.EnumWindows.argtypes = [EnumWindowsProc, wintypes.LPARAM]
user32.FindWindowW.argtypes = [wintypes.LPCWSTR, wintypes.LPCWSTR]
user32.FindWindowExW.argtypes = [
    wintypes.HWND,
    wintypes.HWND,
    wintypes.LPCWSTR,
    wintypes.LPCWSTR,
]
user32.SendMessageTimeoutW.argtypes = [
    wintypes.HWND,
    wintypes.UINT,
    wintypes.WPARAM,
    wintypes.LPARAM,
    wintypes.UINT,
    wintypes.UINT,
    ctypes.POINTER(ULONG_PTR),
]
user32.SetWindowLongPtrW.argtypes = [wintypes.HWND, ctypes.c_int, LONG_PTR]
user32.GetWindowLongPtrW.argtypes = [wintypes.HWND, ctypes.c_int]
user32.SetWindowLongPtrW.restype = LONG_PTR
user32.GetWindowLongPtrW.restype = LONG_PTR
user32.SetParent.argtypes = [wintypes.HWND, wintypes.HWND]
user32.SetWindowPos.argtypes = [
    wintypes.HWND,
    wintypes.HWND,
    ctypes.c_int,
    ctypes.c_int,
    ctypes.c_int,
    ctypes.c_int,
    wintypes.UINT,
]
user32.ShowWindow.argtypes = [wintypes.HWND, ctypes.c_int]


def _get_desktop_host_window():
    progman = user32.FindWindowW("Progman", None)
    result = ULONG_PTR()

    if progman:
        user32.SendMessageTimeoutW(
            progman,
            0x052C,
            0,
            0,
            SMTO_NORMAL,
            1000,
            ctypes.byref(result),
        )

    workerw = {"hwnd": None}

    @EnumWindowsProc
    def enum_windows_callback(hwnd, _lparam):
        shell_view = user32.FindWindowExW(hwnd, None, "SHELLDLL_DefView", None)
        if shell_view:
            candidate = user32.FindWindowExW(None, hwnd, "WorkerW", None)
            if candidate:
                workerw["hwnd"] = candidate
                return False
        return True

    user32.EnumWindows(enum_windows_callback, 0)
    return workerw["hwnd"] or progman


def apply_desktop_window_mode(hwnd):
    desktop_host = _get_desktop_host_window()
    if desktop_host:
        user32.SetParent(hwnd, desktop_host)

    ex_style = user32.GetWindowLongPtrW(hwnd, GWL_EXSTYLE)
    ex_style = (ex_style | WS_EX_TOOLWINDOW) & ~WS_EX_APPWINDOW
    user32.SetWindowLongPtrW(hwnd, GWL_EXSTYLE, ex_style)

    user32.SetWindowPos(
        hwnd,
        HWND_BOTTOM,
        0,
        0,
        0,
        0,
        SWP_NOMOVE | SWP_NOSIZE | SWP_NOACTIVATE | SWP_FRAMECHANGED,
    )
    user32.ShowWindow(hwnd, SW_SHOW)
