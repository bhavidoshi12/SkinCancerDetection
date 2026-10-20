@echo off
title DermaCare AI - Skin Cancer Detection System
cd /d "%~dp0"

echo ======================================================================
echo          Skin Cancer Detection System Using Deep Learning
echo          SVKM's NMIMS MPSTME - Software Engineering Mini-Project
echo ======================================================================
echo.

if not exist "venv\Scripts\python.exe" (
    echo [ERROR] Virtual environment not found!
    echo Please make sure you are in the skin_cancer_detection directory.
    pause
    exit /b
)

echo [1/2] Activating Python environment...
call venv\Scripts\activate.bat

echo [2/2] Launching Flask server at http://127.0.0.1:5000 ...
echo.
echo  Website URL: http://127.0.0.1:5000
echo  Press Ctrl+C in this window anytime to stop the server.
echo.

rem Automatically open browser after 2 seconds
start "" http://127.0.0.1:5000

python app.py
pause
