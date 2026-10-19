@echo off
setlocal
if "%~1"=="" (
  echo Drag a SIIG BBX .bin/.gz file or a folder onto this launcher.
  pause
  exit /b 2
)
set "INPUT=%~1"
set "OUTPUT=%~dpn1_extracted"
py -3 "%~dp0siig_toolkit.py" extract "%INPUT%" -o "%OUTPUT%" --recursive --convert-gltf --convert-tex
if errorlevel 1 (
  echo.
  echo Extraction completed with errors.
) else (
  echo.
  echo Output: "%OUTPUT%"
)
pause
