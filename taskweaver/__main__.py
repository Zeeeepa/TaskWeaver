#!/usr/bin/env python3
"""
TaskWeaver main entry point

This module provides the main entry point for the TaskWeaver package when executed
directly using `python -m taskweaver`. It supports the following command-line options:

CLI Options:
    --web: Launch the web interface (default)
        --host: Specify the host address (default: 0.0.0.0)
        --port: Specify the port number (default: 8000)
    
    --gui: Launch the desktop GUI interface
    
    --cli: Launch the command-line interface
        --project: Specify the project directory
        --interactive: Enable interactive mode
    
    --config: Specify a custom configuration file path
    
    --debug: Enable debug logging
    
    --version: Display version information

Examples:
    python -m taskweaver --web --port 8080
    python -m taskweaver --gui
    python -m taskweaver --cli --project ./my_project --interactive
"""

import sys
from main import main as main_func

def main():
    """
    Main entry point for the taskweaver package
    
    Parses command-line arguments and launches the appropriate interface.
    Returns the exit code from the main function.
    """
    sys.exit(main_func())

if __name__ == "__main__":
    main()
