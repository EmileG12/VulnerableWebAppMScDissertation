@echo off
REM Vulnerable Web Application Launch Script for Windows
REM This batch file sets up the environment and launches the Flask application

setlocal EnableDelayedExpansion

echo.
echo 🚨 VULNERABLE WEB APPLICATION LAUNCHER
echo ==========================================
echo ⚠️  WARNING: This application contains intentional security vulnerabilities!
echo    - CSRF vulnerabilities
echo    - SQL injection vulnerabilities
echo    - Session hijacking vulnerabilities  
echo    - Only use for educational purposes!
echo ==========================================
echo.

REM Get script directory
set "SCRIPT_DIR=%~dp0"
cd /d "%SCRIPT_DIR%"

REM Check if Python is installed
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Error: Python is not installed or not in PATH
    echo Please install Python 3.7+ from https://www.python.org/downloads/
    echo Make sure to check "Add Python to PATH" during installation
    pause
    exit /b 1
)

echo 🐍 Using Python:
python --version

REM Check if pip is available
pip --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Error: pip is not installed
    echo Please reinstall Python with pip included
    pause
    exit /b 1
)

REM Create virtual environment if it doesn't exist
if not exist "venv" (
    echo 📦 Creating virtual environment...
    python -m venv venv
    if !errorlevel! neq 0 (
        echo ❌ Failed to create virtual environment
        pause
        exit /b 1
    )
)

REM Activate virtual environment
echo 🔧 Activating virtual environment...
call venv\Scripts\activate.bat

REM Check if pip needs upgrading
echo 📦 Checking pip version...
for /f "tokens=2" %%i in ('pip --version') do set CURRENT_PIP=%%i
python -c "import requests; r=requests.get('https://pypi.org/pypi/pip/json'); latest=r.json()['info']['version']; current='%CURRENT_PIP%'; print('UPGRADE_NEEDED' if current != latest else 'UP_TO_DATE')" >pip_check.tmp 2>nul
set /p PIP_STATUS=<pip_check.tmp
del pip_check.tmp >nul 2>&1

if "%PIP_STATUS%"=="UPGRADE_NEEDED" (
    echo 📦 Upgrading pip...
    python -m pip install --upgrade pip
) else (
    echo ✅ Pip is already up to date
)

REM Install requirements with check
if exist "requirements.txt" (
    echo 📦 Checking and installing requirements...
    REM Check if packages are already satisfied
    pip check >nul 2>&1
    if !errorlevel! equ 0 (
        echo ✅ All requirements already satisfied
    ) else (
        echo 📦 Installing/updating missing requirements...
        pip install -r requirements.txt --quiet
        if !errorlevel! neq 0 (
            echo ❌ Failed to install requirements
            pause
            exit /b 1
        )
    )
) else (
    echo 📦 Checking Flask installation...
    python -c "import flask; print('Flask version:', flask.__version__)" >nul 2>&1
    if !errorlevel! neq 0 (
        echo 📦 Installing Flask...
        pip install Flask==2.3.3 Werkzeug==2.3.7
        if !errorlevel! neq 0 (
            echo ❌ Failed to install Flask
            pause
            exit /b 1
        )
    ) else (
        echo ✅ Flask is already installed
    )
)

REM Create instance directory
if not exist "instance" mkdir instance

REM Set Flask environment variables
set FLASK_APP=VulnerableApp
set FLASK_ENV=development
set FLASK_DEBUG=1

echo.
echo ✅ Environment setup complete!
echo.
echo 🚀 Starting Vulnerable Web Application...
echo 🌐 Server will be available at: http://localhost:5000
echo 🔑 Default credentials:
echo    Username: Jacksparrow, Password: princess
echo    Username: Barbossa, Password: Blackpearl
echo    Username: Johnnydepp, Password: Pirates
echo.
echo Press Ctrl+C to stop the server
echo.

REM Launch the application using flask run
flask run --host=0.0.0.0 --port=5000

REM Deactivate virtual environment when done  
call venv\Scripts\deactivate.bat

echo.
echo Press any key to exit...
pause >nul
