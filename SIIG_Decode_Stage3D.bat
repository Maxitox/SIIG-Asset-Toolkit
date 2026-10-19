@echo off
setlocal
if "%~1"=="" (
  echo Drag a Bmap/Xmap/map4/map5 file or an extracted stage folder onto this launcher.
  pause
  exit /b 1
)
py -3 "%~dp0siig_toolkit.py" stage3dmap "%~1" -o "%~dpn1_stage3d"
if errorlevel 1 pause
