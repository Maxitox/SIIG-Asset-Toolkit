@echo off
setlocal

if "%~1"=="" (
  echo Drag an Xbox 360 STFS package, PS3 PKG, extracted game ZIP, or game folder onto this file.
  echo.
  echo PS3 note: place the six decrypted .bin.gz.dat files beside the input,
  echo or use the command-line tool with --ps3-sdat-dir.
  echo.
  pause
  exit /b 1
)

where py >nul 2>nul
if not errorlevel 1 (
  set "PY=py -3"
) else (
  where python >nul 2>nul
  if errorlevel 1 (
    echo Python 3.10 or newer was not found on PATH.
    echo Install Python, then run this launcher again.
    pause
    exit /b 2
  )
  set "PY=python"
)

set "INPUT=%~1"
set "OUTPUT=%~dp1SIIG_Ripped"

echo Input:  "%INPUT%"
echo Output: "%OUTPUT%"
echo.

%PY% "%~dp0siig_toolkit.py" rip-game "%INPUT%" -o "%OUTPUT%" --resume
set "CODE=%ERRORLEVEL%"

echo.
if exist "%OUTPUT%\validation\RIP_REPORT.txt" echo Report:   "%OUTPUT%\validation\RIP_REPORT.txt"
if exist "%OUTPUT%\validation\OUTPUT_MANIFEST.json" echo Manifest: "%OUTPUT%\validation\OUTPUT_MANIFEST.json"
if exist "%OUTPUT%\stage_explorer\SIIG_Stage_Explorer.html" echo Explorer: "%OUTPUT%\stage_explorer\SIIG_Stage_Explorer.html"

if not "%CODE%"=="0" echo Extraction failed with exit code %CODE%.
pause
exit /b %CODE%
