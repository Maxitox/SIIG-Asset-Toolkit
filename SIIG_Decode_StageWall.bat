@echo off
setlocal
if "%~1"=="" (
  echo Drag a wall/Xwall/stage_generate file or an extracted stage folder onto this launcher.
  pause
  exit /b 1
)
py -3 "%~dp0siig_toolkit.py" stagewall "%~1" -o "%~dpn1_stagewall"
if errorlevel 1 pause
