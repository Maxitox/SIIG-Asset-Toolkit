@echo off
setlocal
if "%~1"=="" (
  echo Drag a SIIG_Ripped folder or extracted asset folder onto this launcher.
  pause
  exit /b 2
)
set "INPUT=%~1"
set "OUTPUT=%~1\asset_viewer"
py -3 "%~dp0siig_toolkit.py" asset-viewer "%INPUT%" -o "%OUTPUT%"
if errorlevel 1 (
  echo.
  echo Viewer generation failed.
) else (
  echo.
  echo Viewer: "%OUTPUT%\SIIG_Asset_Viewer.html"
  start "" "%OUTPUT%\SIIG_Asset_Viewer.html"
)
pause
