@echo off
setlocal EnableDelayedExpansion

title WinDepot Installer
color 0B

:: ==========================
:: CONFIG
:: ==========================
set "INSTALL_DIR=%USERPROFILE%\Desktop\Appdepot"
set "ZIP_FILE=%TEMP%\windepot_release.zip"
set "URL=https://github.com/andomatthew1234/WinDepot/releases/latest/download/windepot.zip"

cls
echo ==========================================
echo            WINDEPOT INSTALLER
echo ==========================================
echo.
echo Downloading latest release...
echo.

:: ==========================
:: DOWNLOAD
:: ==========================
powershell -Command "Invoke-WebRequest -Uri '%URL%' -OutFile '%ZIP_FILE%'"

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
echo Extracting files to Desktop...

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

:: This loops through the extracted folder to find exactly where setup.bat landed
for /r "%INSTALL_DIR%" %%F in (setup.bat) do (
    set "FOUND=%%F"
    set "FOUND_DIR=%%~dpF"
    goto launch
)

echo.
echo [ERROR] setup.bat was not found in the ZIP.
echo.
echo Make sure your GitHub Release ZIP contains:
echo     setup.bat
echo     store.py
echo     assets/
echo.
pause
exit /b

:: ==========================
:: RUN SETUP
:: ==========================
:launch
echo [OK] Found setup.bat
echo [INFO] Starting setup...
echo.

:: Change the working directory to where setup.bat is located
cd /d "!FOUND_DIR!"

call "!FOUND!"

exit