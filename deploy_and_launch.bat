@echo off
echo ===================================================
echo TaskWeaver Deployment and Launch Script
echo ===================================================

echo.
echo [1/4] Checking for Python installation...
python --version > nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Python is not installed or not in PATH.
    echo Please install Python 3.8 or higher from https://www.python.org/downloads/
    pause
    exit /b 1
)

REM Check Python version to ensure it's 3.8+
for /f "tokens=2" %%i in ('python -c "import sys; print(sys.version.split()[0])"') do set pyver=%%i
for /f "tokens=1,2 delims=." %%a in ("%pyver%") do (
    if %%a LSS 3 (
        echo ERROR: Python 3.8+ is required, but Python %%a.%%b is installed.
        echo Please install Python 3.8 or higher from https://www.python.org/downloads/
        pause
        exit /b 1
    ) else if %%a EQU 3 if %%b LSS 8 (
        echo ERROR: Python 3.8+ is required, but Python %%a.%%b is installed.
        echo Please install Python 3.8 or higher from https://www.python.org/downloads/
        pause
        exit /b 1
    )
)

echo.
echo [2/4] Pulling latest changes from Git repository...
REM Check if Git is installed
git --version > nul 2>&1
if %errorlevel% neq 0 (
    echo WARNING: Git is not installed or not in PATH.
    echo You may not have the latest version of TaskWeaver.
    echo Press any key to continue anyway or Ctrl+C to abort.
    pause > nul
) else (
    git pull
    if %errorlevel% neq 0 (
        echo WARNING: Failed to pull latest changes from Git repository.
        echo You may not have the latest version of TaskWeaver.
        echo Press any key to continue anyway or Ctrl+C to abort.
        pause > nul
    )
)

echo.
echo [3/4] Installing/updating dependencies...
python -m pip install --upgrade pip
if %errorlevel% neq 0 (
    echo ERROR: Failed to upgrade pip.
    pause
    exit /b 1
)
python -m pip install -r requirements.txt
if %errorlevel% neq 0 (
    echo ERROR: Failed to install dependencies.
    pause
    exit /b 1
)

echo.
echo [4/4] Launching TaskWeaver Web UI...
echo.
echo TaskWeaver is starting...
echo You can access the web interface at http://localhost:8000 once it's running.
echo Press Ctrl+C to stop TaskWeaver when you're done.
echo.

python main.py --web --auto-install

echo.
echo TaskWeaver has been stopped.
pause
