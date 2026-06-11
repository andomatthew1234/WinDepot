@echo off
setlocal EnableDelayedExpansion

title WinDepot Installer
color 0B

:: ==========================
:: DYNAMIC DESKTOP DETECTION
:: ==========================
:: This checks the Windows Registry to find your true Desktop path (handles OneDrive seamlessly)
for /f "tokens=2*" %%A in ('reg query "HKCU\Software\Microsoft\Windows\CurrentVersion\Explorer\User Shell Folders" /v Desktop') do (
    set "DESKTOP_RAW=%%B"
)
:: Expand %USERPROFILE% if the registry used an environmental string
for /f "delims=" %%I in ("!DESKTOP_RAW!") do set "TRUE_DESKTOP=%%I"

set "INSTALL_DIR=%TRUE_DESKTOP%\Appdepot"
set "ZIP_FILE=%TEMP%\windepot_release.zip"
set "URL=https://github.com/andomatthew1234/WinDepot/releases/latest/download/windepot.zip"

cls
echo ==========================================
echo            WINDEPOT INSTALLER
echo ==========================================
echo.
echo Resolved Target Desktop: %TRUE_DESKTOP%
echo Downloading latest release...
echo.

:: ==========================
:: DOWNLOAD
:: ==========================
powershell -Command "[Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12; Invoke-WebRequest -Uri '%URL%' -OutFile '%ZIP_FILE%'"

if not exist "%ZIP_FILE%" (
    echo.
    echo [ERROR] Download failed. Check your internet or GitHub URL.
    pause
    exit /b
)

echo [OK] Download complete.
echo.

:: ==========================
:: CLEAN OLD INSTALL
:: ==========================
if exist "%INSTALL_DIR%" (
    echo Removing previous installation...
    rmdir /s /q "%INSTALL_DIR%"
)

mkdir "%INSTALL_DIR%"

:: ==========================
:: EXTRACT
:: ==========================
echo Extracting files to Appdepot...

powershell -Command "Expand-Archive -Force '%ZIP_FILE%' '%INSTALL_DIR%'"

if errorlevel 1 (
    echo.
    echo [ERROR] Extraction failed.
    pause
    exit /b
)

echo [OK] Extraction complete.
echo.

:: ==========================
:: FIND setup.bat
:: ==========================
echo Searching for setup.bat...
set "FOUND="
set "FOUND_DIR="

for /r "%INSTALL_DIR%" %%F in (setup.bat) do (
    set "FOUND=%%F"
    set "FOUND_DIR=%%~dpF"
    goto launch
)

echo.
echo [ERROR] setup.bat was not found in the ZIP.
pause
exit /b

:: ==========================
:: RUN SETUP
:: ==========================
:launch
echo [OK] Found setup.bat
echo [INFO] Starting setup...
echo.

cd /d "!FOUND_DIR!"
call "!FOUND!"

exit