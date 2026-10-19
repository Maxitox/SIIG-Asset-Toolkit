@echo off
setlocal
if "%~1"=="" (
  echo Drag an extracted shader blob or shader folder onto this launcher.
  pause
  exit /b 1
)
py -3 "%~dp0siig_toolkit.py" shader-info "%~1" -o "%~dpn1_shader_info"
if errorlevel 1 pause
