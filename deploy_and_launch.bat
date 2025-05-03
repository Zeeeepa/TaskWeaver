@echo off
REM TaskWeaver Deployment and Launch Script for Windows

echo TaskWeaver Deployment and Launch Script
echo ========================================

REM Check if Python is installed
python --version >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo Error: Python is not installed or not in PATH. Please install Python and try again.
    exit /b 1
)

REM Check if pip is installed
pip --version >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo Error: pip is not installed or not in PATH. Please install pip and try again.
    exit /b 1
)

REM Check if git is installed
git --version >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo Error: git is not installed or not in PATH. Please install git and try again.
    exit /b 1
)

REM Pull the latest changes
echo Pulling the latest changes from the repository...
git pull

REM Create a virtual environment if it doesn't exist
if not exist venv (
    echo Creating a virtual environment...
    python -m venv venv
)

REM Activate the virtual environment
echo Activating the virtual environment...
call venv\Scripts\activate.bat

REM Install or upgrade dependencies
echo Installing or upgrading dependencies...
pip install -e .[dev]

REM Check if the installation was successful
if %ERRORLEVEL% NEQ 0 (
    echo Error: Failed to install dependencies. Please check the error message above.
    exit /b 1
)

REM Set up environment variables
echo Setting up environment variables...

REM Check if .env file exists
if exist .env (
    echo Found .env file. Loading environment variables...
    for /f "tokens=*" %%a in (.env) do (
        set %%a
    )
) else (
    echo No .env file found. Creating a new one...
    
    REM Prompt for API keys
    set /p OPENAI_API_KEY=Enter your OpenAI API key (leave blank to skip): 
    set /p CODEGEN_API_KEY=Enter your Codegen API key (leave blank to skip): 
    set /p CODEGEN_ORG_ID=Enter your Codegen organization ID (leave blank to skip): 
    set /p GITHUB_TOKEN=Enter your GitHub token (leave blank to skip): 
    set /p NGROK_TOKEN=Enter your ngrok token (leave blank to skip): 
    
    REM Create .env file
    echo # TaskWeaver Environment Variables > .env
    if defined OPENAI_API_KEY echo OPENAI_API_KEY=%OPENAI_API_KEY% >> .env
    if defined CODEGEN_API_KEY echo CODEGEN_API_KEY=%CODEGEN_API_KEY% >> .env
    if defined CODEGEN_ORG_ID echo CODEGEN_ORG_ID=%CODEGEN_ORG_ID% >> .env
    if defined GITHUB_TOKEN echo GITHUB_TOKEN=%GITHUB_TOKEN% >> .env
    if defined NGROK_TOKEN echo NGROK_TOKEN=%NGROK_TOKEN% >> .env
)

REM Launch TaskWeaver
echo Launching TaskWeaver...
echo ========================================

REM Prompt for launch mode
echo Select a launch mode:
echo 1. Web UI (default)
echo 2. Desktop GUI
echo 3. CLI
set /p LAUNCH_MODE=Enter your choice (1-3): 

REM Set default port
set PORT=8000

REM Prompt for port
set /p PORT_INPUT=Enter port number (default: 8000): 
if defined PORT_INPUT set PORT=%PORT_INPUT%

REM Launch based on selected mode
if "%LAUNCH_MODE%"=="2" (
    echo Launching Desktop GUI...
    python main.py --gui
) else if "%LAUNCH_MODE%"=="3" (
    echo Launching CLI...
    set /p PROJECT_DIR=Enter project directory: 
    if not defined PROJECT_DIR (
        echo Error: Project directory is required for CLI mode.
        exit /b 1
    )
    python main.py --cli --project "%PROJECT_DIR%" --interactive
) else (
    echo Launching Web UI on port %PORT%...
    python main.py --web --port %PORT%
)

REM Deactivate the virtual environment when done
deactivate

