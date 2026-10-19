@echo off
setlocal
if "%~1"=="" (
  echo Drag a completed SIIG_Ripped folder onto this file.
  echo.
  echo The updater reuses the rip's retained decompressed_bbx sources and does not
  echo require the original Xbox 360 STFS, PS3 PKG, ZIP, or extracted game folder.
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
    pause
    exit /b 2
  )
  set "PY=python"
)
%PY% "%~dp0siig_toolkit.py" update-rip "%~1"
set "CODE=%ERRORLEVEL%"
echo.
if "%CODE%"=="0" (
  echo Rip update completed successfully.
) else (
  echo Rip update failed with exit code %CODE%.
)
if exist "%~1\validation\RIP_UPDATE_REPORT.json" echo Report: "%~1\validation\RIP_UPDATE_REPORT.json"
pause
exit /b %CODE%
