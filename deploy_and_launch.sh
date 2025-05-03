#!/bin/bash
# TaskWeaver deployment and launch script for Linux/macOS

# Set up virtual environment
echo "Setting up virtual environment..."
python -m venv venv
source venv/bin/activate

# Install dependencies
echo "Installing dependencies..."
pip install --upgrade pip setuptools wheel
pip install -e .

# Create logs directory
echo "Creating logs directory..."
mkdir -p logs

# Set environment variables
echo "Setting environment variables..."
export PYTHONPATH=$(pwd)
export TASKWEAVER_CONFIG=$(pwd)/standalone_taskweaver/cli/project/config.yaml

# Launch TaskWeaver
echo "Launching TaskWeaver..."
python -m standalone_taskweaver --debug

# Deactivate virtual environment on exit
deactivate

