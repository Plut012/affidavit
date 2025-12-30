@echo off
REM Update script for Affidavit Writing Assistant (Windows)

echo ========================================
echo   Affidavit Assistant - Update
echo ========================================
echo.

echo Pulling latest changes from GitHub...
git pull

IF ERRORLEVEL 1 (
    echo.
    echo ERROR: Failed to pull updates from GitHub
    echo Make sure you have internet connection and git is configured
    pause
    exit /b 1
)

echo.
echo Update complete!
echo.
echo Checking for dependency updates...

REM Activate virtual environment and update dependencies
if exist venv\Scripts\activate.bat (
    call venv\Scripts\activate.bat
    pip install -r requirements.txt --quiet
    echo Dependencies updated.
    deactivate
) else (
    echo Note: Virtual environment not found. Run setup first.
)

echo.
echo ========================================
echo   Update finished successfully!
echo ========================================
echo.
pause
