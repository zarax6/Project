import ctypes
from ctypes import wintypes


user32 = ctypes.WinDLL("user32", use_last_error=True)

LONG_PTR = ctypes.c_longlong if ctypes.sizeof(ctypes.c_void_p) == 8 else ctypes.c_long

GWL_EXSTYLE = -20
SWP_NOMOVE = 0x0002
SWP_NOSIZE = 0x0001
SWP_NOACTIVATE = 0x0010
SWP_FRAMECHANGED = 0x0020
SW_SHOWNA = 8
HWND_BOTTOM = 1
WS_EX_APPWINDOW = 0x00040000
WS_EX_TOOLWINDOW = 0x00000080


user32.SetWindowLongPtrW.argtypes = [wintypes.HWND, ctypes.c_int, LONG_PTR]
user32.GetWindowLongPtrW.argtypes = [wintypes.HWND, ctypes.c_int]
user32.SetWindowLongPtrW.restype = LONG_PTR
user32.GetWindowLongPtrW.restype = LONG_PTR
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


def apply_desktop_window_mode(hwnd):
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
    user32.ShowWindow(hwnd, SW_SHOWNA)
