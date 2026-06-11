@echo off
title WinDepot Setup Installer
color 0B

cls
echo ================================
echo         WINDEPOT SETUP
echo ================================
echo.

echo Checking Python installation...
timeout /t 1 >nul

:: Check Python (py launcher)
py --version >nul 2>&1
if %errorlevel%==0 goto install_deps

:: Check python command
python --version >nul 2>&1
if %errorlevel%==0 (
    set "PY_CMD=python"
    goto install_deps
)

:: Not found -> launch installer
echo.
echo [!] Python not found
echo [-] Launching Python installer...

:: Make sure python_installer.exe is in the same folder as setup.bat in your ZIP
if exist "%~dp0python_installer.exe" (
    start "" "%~dp0python_installer.exe"
) else (
    echo [ERROR] python_installer.exe is missing from the folder!
    pause
    exit /b
)

echo.
echo We're installing the Python software for you so you can use the app.
echo When it finishes, press any key to continue the installer.
pause >nul

goto check

:: ================================
:: RE-CHECK LOOP
:: ================================
:check
py --version >nul 2>&1
if %errorlevel%==0 goto install_deps

python --version >nul 2>&1
if %errorlevel%==0 goto install_deps

echo.
echo We still couldn't detect Python on your system. You can try again, or manually install Python from:
echo https://apps.microsoft.com/detail/9ncvdn91xzqp
echo Please finish installation, then press any key to try again.
pause >nul
goto check

:: ================================
:: INSTALL DEPENDENCIES
:: ================================
:install_deps
echo.
echo [OK] Python detected.
echo Installing required libraries (CustomTkinter, Pillow)...
echo.

:: Use 'py' or 'python' based on what worked
py -m pip install --upgrade pip >nul 2>&1
py -m pip install customtkinter Pillow

echo [OK] Dependencies installed successfully.

:: ================================
:: CREATE DESKTOP SHORTCUT
:: ================================
echo.
echo Creating Desktop Shortcut...

:: We use PowerShell to generate a native .lnk shortcut on the user's desktop
:: Note: It looks for favicon.ico in the current directory!
set "SHORTCUT_PATH=%USERPROFILE%\Desktop\WinDepot.lnk"
set "TARGET_SCRIPT=%~dp0store.py"
set "WORK_DIR=%~dp0"
set "ICON_PATH=%~dp0favicon.ico"

powershell -Command "$WshShell = New-Object -comObject WScript.Shell; $Shortcut = $WshShell.CreateShortcut('%SHORTCUT_PATH%'); $Shortcut.TargetPath = 'pythonw.exe'; $Shortcut.Arguments = '\"%TARGET_SCRIPT%\"'; $Shortcut.WorkingDirectory = '%WORK_DIR%'; $Shortcut.IconLocation = '%ICON_PATH%'; $Shortcut.Save()"

echo [OK] Shortcut created on Desktop.

:: ================================
:: READY STATE & LAUNCH
:: ================================
cls
echo ================================
echo         WINDEPOT SETUP
echo ================================
echo.
echo [OK] Python detected
echo [OK] Libraries updated
echo [OK] Shortcut generated
echo.
echo Setup is fully complete! Launching WinDepot now...
echo.
timeout /t 2 >nul

:: Launch using pythonw to hide the background CMD console
start "" pythonw "%~dp0store.py"

exit