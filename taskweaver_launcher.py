#!/usr/bin/env python3
"""
TaskWeaver Launcher - Choose between CLI and GUI modes
"""

import os
import sys
import subprocess
import argparse


def check_dependencies():
    """Check if all required dependencies are installed"""
    try:
        import injector
        import tiktoken
        import yaml
        import typing_extensions
        import uuid
        
        # Check for PyQt5 (only needed for GUI)
        try:
            import PyQt5
            has_pyqt = True
        except ImportError:
            has_pyqt = False
        
        return True, has_pyqt
    except ImportError as e:
        return False, False


def install_dependencies():
    """Install required dependencies"""
    print("Installing required dependencies...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("Dependencies installed successfully!")
        return True
    except subprocess.CalledProcessError:
        print("Failed to install dependencies. Please install them manually:")
        print("pip install -r requirements.txt")
        return False


def main():
    parser = argparse.ArgumentParser(description="TaskWeaver Launcher")
    parser.add_argument("--cli", action="store_true", help="Launch in CLI mode")
    parser.add_argument("--gui", action="store_true", help="Launch in GUI mode")
    args = parser.parse_args()
    
    # Check dependencies
    deps_installed, has_pyqt = check_dependencies()
    
    if not deps_installed:
        print("Missing required dependencies.")
        if input("Would you like to install them now? (y/n): ").lower() == 'y':
            if not install_dependencies():
                return
        else:
            print("Please install the required dependencies and try again.")
            return
    
    # Determine launch mode
    if args.cli:
        mode = "cli"
    elif args.gui:
        mode = "gui"
    else:
        print("TaskWeaver Launcher")
        print("===================")
        print("1. CLI Mode - Command Line Interface")
        print("2. GUI Mode - Graphical User Interface")
        
        choice = input("Select mode (1/2): ").strip()
        mode = "cli" if choice == "1" else "gui"
    
    # Launch the selected mode
    if mode == "cli":
        print("Launching TaskWeaver CLI...")
        subprocess.call([sys.executable, "example_usage.py"])
    else:
        if not has_pyqt:
            print("PyQt5 is required for GUI mode but not installed.")
            if input("Would you like to install it now? (y/n): ").lower() == 'y':
                try:
                    subprocess.check_call([sys.executable, "-m", "pip", "install", "PyQt5>=5.15.0", "PyQt5-stubs>=5.15.0"])
                    print("PyQt5 installed successfully!")
                except subprocess.CalledProcessError:
                    print("Failed to install PyQt5. Please install it manually:")
                    print("pip install PyQt5>=5.15.0 PyQt5-stubs>=5.15.0")
                    return
            else:
                print("Please install PyQt5 and try again.")
                return
        
        print("Launching TaskWeaver GUI...")
        subprocess.call([sys.executable, "taskweaver_gui.py"])


if __name__ == "__main__":
    main()

