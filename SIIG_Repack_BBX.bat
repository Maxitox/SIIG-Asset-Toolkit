@echo off
setlocal
if "%~1"=="" (
  echo Drag a BBX extraction folder containing manifest.json onto this launcher.
  pause
  exit /b 2
)
set "INPUT=%~1"
for %%I in ("%INPUT%") do set "OUTPUT=%%~dpI%%~nxI_repacked.bin"
py -3 "%~dp0siig_toolkit.py" repack-bbx "%INPUT%" -o "%OUTPUT%"
if errorlevel 1 (
  echo.
  echo Repacking failed. The original extraction was not changed.
) else (
  echo.
  echo Repacked archive: "%OUTPUT%"
  echo Keep the original game files unchanged and test modifications on a copy.
)
pause
