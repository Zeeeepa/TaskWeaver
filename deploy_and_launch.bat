@echo off
REM TaskWeaver deployment and launch script for Windows

REM Set up virtual environment
echo Setting up virtual environment...
python -m venv venv
call venv\Scripts\activate.bat

REM Install dependencies
echo Installing dependencies...
pip install --upgrade pip setuptools wheel
pip install -e .

REM Create logs directory
echo Creating logs directory...
if not exist logs mkdir logs

REM Set environment variables
echo Setting environment variables...
set PYTHONPATH=%CD%
set TASKWEAVER_CONFIG=%CD%\standalone_taskweaver\cli\project\config.yaml

REM Launch TaskWeaver
echo Launching TaskWeaver...
python -m standalone_taskweaver --debug

REM Deactivate virtual environment on exit
deactivate

