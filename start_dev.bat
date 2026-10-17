@echo off
setlocal
cd /d "%~dp0"

REM Detect virtual environment python
if exist "scraperenv\Scripts\python.exe" (
    set "PYTHON_CMD=scraperenv\Scripts\python.exe"
) else if exist ".venv\Scripts\python.exe" (
    set "PYTHON_CMD=.venv\Scripts\python.exe"
) else if exist "venv\Scripts\python.exe" (
    set "PYTHON_CMD=venv\Scripts\python.exe"
) else (
    set "PYTHON_CMD=python"
)

"%PYTHON_CMD%" run_dev.py %*

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo Script ended with exit code %ERRORLEVEL%.
    pause
)
