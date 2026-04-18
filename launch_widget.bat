@echo off
setlocal EnableExtensions EnableDelayedExpansion
chcp 65001 >nul

cd /d "%~dp0"

set "PROJECT_DIR=%~dp0"
if "%PROJECT_DIR:~-1%"=="\" set "PROJECT_DIR=%PROJECT_DIR:~0,-1%"
set "APP_SCRIPT=%PROJECT_DIR%\FireFox.py"
set "STARTUP_DIR=%APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup"
set "STARTUP_FILE=%STARTUP_DIR%\DesktopWidget_Autostart.bat"

call :detect_python
if errorlevel 1 goto :fail

echo Проверяю зависимости...
call :ensure_module PyQt6 PyQt6
if errorlevel 1 goto :fail
call :ensure_module PySide6 PySide6
if errorlevel 1 goto :fail

echo.
set /p AUTOSTART=Сделать автозагрузку? y/n: 
if /I "%AUTOSTART%"=="y" (
    call :create_autostart
) else (
    if exist "%STARTUP_FILE%" (
        del "%STARTUP_FILE%"
        echo Автозагрузка отключена.
    ) else (
        echo Автозагрузка не включалась.
    )
)

echo.
echo Запускаю виджет...
start "" "%PYTHONW_EXE%" "%APP_SCRIPT%"
exit /b 0

:detect_python
set "PYTHON_CMD="
set "PYTHONW_EXE="

where py >nul 2>nul
if not errorlevel 1 (
    set "PYTHON_CMD=py -3"
    for /f "usebackq delims=" %%I in (`py -3 -c "import sys; print(sys.executable)"`) do set "PYTHON_EXE=%%I"
)

if not defined PYTHON_CMD (
    where python >nul 2>nul
    if not errorlevel 1 (
        set "PYTHON_CMD=python"
        for /f "usebackq delims=" %%I in (`python -c "import sys; print(sys.executable)"`) do set "PYTHON_EXE=%%I"
    )
)

if not defined PYTHON_CMD (
    echo Python не найден. Установите Python 3 и повторите запуск.
    exit /b 1
)

set "PYTHONW_EXE=%PYTHON_EXE:python.exe=pythonw.exe%"
if not exist "%PYTHONW_EXE%" set "PYTHONW_EXE=%PYTHON_EXE%"
exit /b 0

:ensure_module
set "IMPORT_NAME=%~1"
set "PACKAGE_NAME=%~2"

%PYTHON_CMD% -c "import %IMPORT_NAME%" >nul 2>nul
if not errorlevel 1 (
    echo %PACKAGE_NAME% уже установлен.
    exit /b 0
)

echo %PACKAGE_NAME% не найден. Устанавливаю...
%PYTHON_CMD% -m pip install %PACKAGE_NAME%
if errorlevel 1 (
    echo Не удалось установить %PACKAGE_NAME%.
    exit /b 1
)

exit /b 0

:create_autostart
if not exist "%STARTUP_DIR%" mkdir "%STARTUP_DIR%"
(
    echo @echo off
    echo cd /d "%PROJECT_DIR%"
    echo start "" "%PYTHONW_EXE%" "%APP_SCRIPT%"
) > "%STARTUP_FILE%"
echo Автозагрузка включена: "%STARTUP_FILE%"
exit /b 0

:fail
echo.
echo Настройка не завершена.
exit /b 1
