@echo off
title Snake Battle Arena Server
echo ========================================
echo    SNAKE BATTLE ARENA SERVER
echo ========================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python from https://python.org
    pause
    exit /b 1
)

REM Install requirements if needed
echo Checking dependencies...
pip install -r requirements.txt

REM Start the application
echo.
echo Starting Snake Battle Arena...
echo.
python launcher.py

pause
