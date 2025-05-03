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

echo.
echo [2/4] Pulling latest changes from Git repository...
git pull
if %errorlevel% neq 0 (
    echo WARNING: Failed to pull latest changes from Git repository.
    echo You may not have the latest version of TaskWeaver.
    echo Press any key to continue anyway or Ctrl+C to abort.
    pause > nul
)

echo.
echo [3/4] Installing/updating dependencies...
python -m pip install --upgrade pip
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

