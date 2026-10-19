@echo off
setlocal
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
%PY% "%~dp0siig_gui.py"
if errorlevel 1 pause
