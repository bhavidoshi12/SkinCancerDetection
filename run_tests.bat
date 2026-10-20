@echo off
title DermaCare AI - Automated Test Suite
cd /d "%~dp0"

echo ======================================================================
echo    Running Automated Software Engineering Tests (TC-01 to TC-04)
echo ======================================================================
echo.

call venv\Scripts\activate.bat
python -m pytest -v
echo.
echo ======================================================================
echo Testing complete! Press any key to close this window.
echo ======================================================================
pause
