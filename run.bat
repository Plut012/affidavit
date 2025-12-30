@echo off
REM Launcher script for Affidavit Writing Assistant (Windows)

echo Starting Affidavit Writing Assistant...
echo.

REM Activate virtual environment
if exist venv\Scripts\activate.bat (
    call venv\Scripts\activate.bat
) else (
    echo ERROR: Virtual environment not found!
    echo Please run setup first:
    echo   python -m venv venv
    echo   venv\Scripts\activate
    echo   pip install -r requirements.txt
    echo.
    pause
    exit /b 1
)

REM Run the application
python main.py

REM Deactivate on exit
deactivate

pause
