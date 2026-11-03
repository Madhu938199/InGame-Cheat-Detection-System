@echo off
title Multiplayer In-Game Cheat Detection System
color 0B

echo ======================================================================
echo    STARTING MULTIPLAYER IN-GAME CHEAT DETECTION SYSTEM
echo ======================================================================
echo.

cd /d "%~dp0"

echo [1/3] Checking Python installation...
where py >nul 2>&1
if %ERRORLEVEL% EQU 0 (
    set PY_CMD=py
) else (
    where python >nul 2>&1
    if %ERRORLEVEL% EQU 0 (
        set PY_CMD=python
    ) else (
        echo [ERROR] Python was not found in PATH!
        echo Please install Python 3.9+ from https://www.python.org/
        pause
        exit /b 1
    )
)

echo [2/3] Verifying database and ML artifacts...
%PY_CMD% setup_project.py

echo.
echo [3/3] Launching Flask backend server on http://127.0.0.1:5000 ...
echo.
echo ======================================================================
echo    The web application will open in your browser automatically!
echo    Press Ctrl+C in this terminal window to stop the server anytime.
echo ======================================================================
echo.

start "" "http://127.0.0.1:5000"

%PY_CMD% backend/app.py

pause
