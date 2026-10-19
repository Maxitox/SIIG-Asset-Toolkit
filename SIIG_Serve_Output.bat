@echo off
setlocal
if "%~1"=="" (
  echo Drag a SIIG_Ripped or viewer folder onto this launcher.
  pause
  exit /b 2
)
py -3 "%~dp0siig_toolkit.py" serve "%~1"
