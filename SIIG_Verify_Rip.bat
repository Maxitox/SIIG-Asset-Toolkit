@echo off
setlocal
if "%~1"=="" (
  echo Drag a completed SIIG_Ripped folder onto this file.
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
%PY% "%~dp0siig_toolkit.py" verify-output "%~1"
set "CODE=%ERRORLEVEL%"
echo.
if "%CODE%"=="0" (echo Verification passed.) else (echo Verification failed with exit code %CODE%.)
pause
exit /b %CODE%
