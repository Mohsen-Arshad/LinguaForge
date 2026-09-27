@echo off
setlocal
cd /d "%~dp0"

if not exist ".venv\Scripts\python.exe" (
    echo LinguaForge is not set up yet.
    echo Run setup.bat first.
    pause
    exit /b 1
)

".venv\Scripts\python.exe" run.py

if errorlevel 1 (
    echo.
    echo LinguaForge exited with an error.
    pause
)

endlocal
