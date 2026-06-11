@echo off
setlocal EnableDelayedExpansion

:: ==========================================
:: ANTI-LOCK ENGINE RELOCATION
:: ==========================================
:: Copies script to TEMP directory to prevent Windows from blocking the deletion of the Appdepot folder
if /I not "%~dp0"=="%TEMP%\" (
    echo [SYSTEM] Relocating updater to safe temporary memory...
    copy /y "%~f0" "%TEMP%\windepot_updater.bat" >nul
    start "" "%TEMP%\windepot_updater.bat"
    exit
)

title WinDepot Auto-Updater
color 0E

:: Wait for Python to close and release file locks
echo Waiting for WinDepot environment to exit...
timeout /t 3 /nobreak >nul

:: ==========================================
:: TARGET PATH RESOLUTION
:: ==========================================
for /f "tokens=2*" %%A in ('reg query "HKCU\Software\Microsoft\Windows\CurrentVersion\Explorer\User Shell Folders" /v Desktop') do (
    set "DESKTOP_RAW=%%B"
)
for /f "delims=" %%I in ("!DESKTOP_RAW!") do set "TRUE_DESKTOP=%%I"

set "INSTALL_DIR=%TRUE_DESKTOP%\Appdepot"
set "ZIP_FILE=%TEMP%\windepot_update.zip"
set "URL=https://github.com/andomatthew1234/WinDepot/releases/latest/download/windepot.zip"

cls
echo ==========================================
echo           WINDEPOT AUTO-UPDATER
echo ==========================================
echo.
echo Target Architecture: %INSTALL_DIR%
echo Fetching latest release package from GitHub...
echo.

:: ==========================================
:: FETCH & WIPE
:: ==========================================
powershell -Command "[Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12; Invoke-WebRequest -Uri '%URL%' -OutFile '%ZIP_FILE%'"

if not exist "%ZIP_FILE%" (
    echo [ERROR] Update download failed. Check your internet connection.
    pause
    exit /b
)

echo [OK] Package fetched successfully.
echo.

if exist "%INSTALL_DIR%" (
    echo Wiping legacy application files...
    rmdir /s /q "%INSTALL_DIR%"
)
mkdir "%INSTALL_DIR%"

:: ==========================================
:: DEPLOY & LAUNCH
:: ==========================================
echo Extracting updated manifest...
powershell -Command "Expand-Archive -Force '%ZIP_FILE%' '%INSTALL_DIR%'"

if errorlevel 1 (
    echo [ERROR] Package extraction failed.
    pause
    exit /b
)

echo [OK] Update applied seamlessly.
echo.
echo Initializing WinDepot...

:: Dynamically locate store.py
set "FOUND_DIR="
for /r "%INSTALL_DIR%" %%F in (store.py) do (
    set "FOUND_DIR=%%~dpF"
    goto launch
)

echo [ERROR] store.py not found in the updated package!
pause
exit /b

:launch
cd /d "!FOUND_DIR!"

:: Bypass setup and background launch the newly updated store
start "" pythonw store.py

:: Self-destruct temporary updater files
del "%TEMP%\windepot_update.zip"
del "%~f0"
exit