#!/usr/bin/env python3
"""
TaskWeaver Main Launcher

This is the main entry point for TaskWeaver with a fully featured UI.
It provides options to launch different UI modes:
- Web UI: A web-based interface with Codegen integration
- GUI: A PyQt5-based desktop interface
- CLI: A command-line interface for scripting and automation

Usage:
    python main.py --web      # Launch the web UI
    python main.py --gui      # Launch the desktop GUI
    python main.py --cli      # Launch the CLI interface
"""

import os
import sys
import argparse
import logging
import subprocess
import importlib.metadata
from typing import Dict, Optional, List, Any, Tuple

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("taskweaver")

# Version information
try:
    __version__ = importlib.metadata.version("taskweaver")
except importlib.metadata.PackageNotFoundError:
    __version__ = "unknown"

def parse_args():
    """
    Parse command line arguments
    """
    parser = argparse.ArgumentParser(
        description="TaskWeaver - A code-first agent framework for data analytics tasks",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    
    # UI mode selection
    mode_group = parser.add_argument_group("UI Mode")
    mode_exclusive = mode_group.add_mutually_exclusive_group()
    mode_exclusive.add_argument("--web", action="store_true", help="Launch the web UI")
    mode_exclusive.add_argument("--gui", action="store_true", help="Launch the desktop GUI")
    mode_exclusive.add_argument("--cli", action="store_true", help="Launch the CLI interface")
    
    # Web UI options
    web_group = parser.add_argument_group("Web UI Options")
    web_group.add_argument("--host", default="0.0.0.0", help="Host to bind the web server to")
    web_group.add_argument("--port", type=int, default=8000, help="Port to bind the web server to")
    
    # CLI options
    cli_group = parser.add_argument_group("CLI Options")
    cli_group.add_argument("--project", type=str, help="Project directory path for CLI mode (required when using --cli)")
    cli_group.add_argument("--interactive", action="store_true", help="Run CLI in interactive mode")
    
    # Common options
    common_group = parser.add_argument_group("Common Options")
    common_group.add_argument("--config", type=str, help="Path to configuration file")
    common_group.add_argument("--debug", action="store_true", help="Enable debug logging")
    common_group.add_argument("--version", action="store_true", help="Display version information and exit")
    common_group.add_argument("--auto-install", action="store_true", help="Automatically install missing dependencies")
    
    return parser.parse_args()

def install_package(package: str) -> Tuple[bool, str]:
    """
    Install a Python package using pip
    
    Args:
        package: Package name or installation string (e.g., "PyQt5" or "-e .")
        
    Returns:
        Tuple of (success, message)
    """
    try:
        logger.info(f"Installing {package}...")
        subprocess.check_call([sys.executable, "-m", "pip", "install"] + package.split())
        return True, f"Successfully installed {package}"
    except subprocess.CalledProcessError as e:
        return False, f"Failed to install {package}: {str(e)}"

def launch_web_ui(host: str = "0.0.0.0", port: int = 8000, config_path: Optional[str] = None, auto_install: bool = False):
    """
    Launch the web UI
    
    Args:
        host: Host to bind the web server to
        port: Port to bind the web server to
        config_path: Path to configuration file
        auto_install: Whether to automatically install missing dependencies
    """
    try:
        from standalone_taskweaver.ui.server import run_server
        
        logger.info(f"Starting TaskWeaver Web UI on http://{host}:{port}")
        logger.info("Press Ctrl+C to stop the server")
        
        # Apply configuration if provided
        if config_path:
            if not os.path.exists(config_path):
                logger.error(f"Configuration file not found: {config_path}")
                return 1
            os.environ["TASKWEAVER_CONFIG_PATH"] = config_path
            logger.info(f"Using configuration from {config_path}")
        
        run_server(host=host, port=port)
        return 0
    except ImportError as e:
        logger.error(f"Failed to import web UI components: {str(e)}")
        
        if auto_install:
            logger.info("Attempting to install missing dependencies...")
            success, message = install_package("-e .")
            if success:
                logger.info(f"{message}. Please rerun the script.")
                logger.info("You can now run: python main.py --web")
            else:
                logger.error(message)
                logger.error("Please install dependencies manually: pip install -e .")
                logger.error("For more information, see the project documentation.")
        else:
            logger.error("Make sure all dependencies are installed: pip install -e .")
            logger.error("Use --auto-install to automatically install dependencies")
        
        return 1
    except Exception as e:
        logger.error(f"Error launching web UI: {str(e)}")
        return 1

def launch_gui(config_path: Optional[str] = None, auto_install: bool = False):
    """
    Launch the desktop GUI
    
    Args:
        config_path: Path to configuration file
        auto_install: Whether to automatically install missing dependencies
    """
    try:
        from PyQt5.QtWidgets import QApplication
        from taskweaver_gui import TaskWeaverGUI
        
        logger.info("Starting TaskWeaver Desktop GUI")
        
        # Apply configuration if provided
        if config_path:
            if not os.path.exists(config_path):
                logger.error(f"Configuration file not found: {config_path}")
                return 1
            os.environ["TASKWEAVER_CONFIG_PATH"] = config_path
            logger.info(f"Using configuration from {config_path}")
        
        app = QApplication(sys.argv)
        gui = TaskWeaverGUI()
        gui.show()
        return app.exec_()
    except ImportError as e:
        logger.error(f"Failed to import GUI components: {str(e)}")
        
        if auto_install:
            logger.info("Attempting to install missing dependencies...")
            success, message = install_package("PyQt5")
            if success:
                logger.info(f"{message}. Please rerun the script.")
                logger.info("You can now run: python main.py --gui")
            else:
                logger.error(message)
                logger.error("Please install PyQt5 manually: pip install PyQt5")
                logger.error("For more information, see the project documentation.")
        else:
            logger.error("Make sure PyQt5 is installed: pip install PyQt5")
            logger.error("Use --auto-install to automatically install dependencies")
        
        return 1
    except Exception as e:
        logger.error(f"Error launching GUI: {str(e)}")
        return 1

def launch_cli(project_dir: Optional[str] = None, interactive: bool = False, 
               config_path: Optional[str] = None, auto_install: bool = False):
    """
    Launch the CLI interface
    
    Args:
        project_dir: Project directory path
        interactive: Whether to run in interactive mode
        config_path: Path to configuration file
        auto_install: Whether to automatically install missing dependencies
    """
    try:
        from taskweaver_launcher import TaskWeaverCLI
        
        logger.info("Starting TaskWeaver CLI")
        
        # Apply configuration if provided
        if config_path:
            if not os.path.exists(config_path):
                logger.error(f"Configuration file not found: {config_path}")
                return 1
            os.environ["TASKWEAVER_CONFIG_PATH"] = config_path
            logger.info(f"Using configuration from {config_path}")
        
        cli = TaskWeaverCLI()
        
        if not project_dir:
            logger.error("Project directory is required for CLI mode")
            raise ValueError("Project directory is required for CLI mode. Use --project to specify a project directory.")
        
        if interactive:
            logger.info(f"Running in interactive mode with project directory: {project_dir}")
            cli.run_interactive(project_dir)
            return 0
        else:
            # Initialize and return
            success = cli.initialize(project_dir)
            return 0 if success else 1
    except ImportError as e:
        logger.error(f"Failed to import CLI components: {str(e)}")
        
        if auto_install:
            logger.info("Attempting to install missing dependencies...")
            success, message = install_package("-e .")
            if success:
                logger.info(f"{message}. Please rerun the script.")
                logger.info("You can now run: python main.py --cli --project <project_dir>")
            else:
                logger.error(message)
                logger.error("Please install dependencies manually: pip install -e .")
                logger.error("For more information, see the project documentation.")
        else:
            logger.error("Make sure all dependencies are installed: pip install -e .")
            logger.error("Use --auto-install to automatically install dependencies")
        
        return 1
    except ValueError as e:
        logger.error(str(e))
        return 1
    except Exception as e:
        logger.error(f"Error launching CLI: {str(e)}")
        return 1

def setup_environment(debug: bool = False, config_path: Optional[str] = None):
    """
    Set up the environment for TaskWeaver
    
    Args:
        debug: Whether to enable debug logging
        config_path: Path to configuration file
        
    Returns:
        bool: True if environment setup was successful, False otherwise
    """
    # Set up logging level
    if debug:
        logging.getLogger().setLevel(logging.DEBUG)
        logger.debug("Debug logging enabled")
    
    # Apply configuration if provided
    if config_path:
        if not os.path.exists(config_path):
            logger.warning(f"Configuration file not found: {config_path}")
            return False
        elif not os.access(config_path, os.R_OK):
            logger.warning(f"Configuration file not readable: {config_path}")
            return False
        else:
            os.environ["TASKWEAVER_CONFIG_PATH"] = config_path
            logger.debug(f"Using configuration from {config_path}")
    
    # Check for required environment variables
    if not os.environ.get("OPENAI_API_KEY"):
        logger.warning("OPENAI_API_KEY environment variable not set")
        logger.warning("You may need to set this for TaskWeaver to function properly")
        logger.warning("Example: export OPENAI_API_KEY=your_api_key_here")
    
    # Check for other optional but recommended environment variables
    if not os.environ.get("OPENAI_API_BASE"):
        logger.debug("OPENAI_API_BASE not set, using default OpenAI API endpoint")
    
    if not os.environ.get("OPENAI_MODEL"):
        logger.debug("OPENAI_MODEL not set, using default model")
    
    return True

def display_version():
    """
    Display version information
    """
    print(f"TaskWeaver version: {__version__}")
    print("A code-first agent framework for data analytics tasks")
    print("https://github.com/microsoft/TaskWeaver")

def main():
    """
    Main entry point
    """
    # Parse command line arguments
    args = parse_args()
    
    # Display version and exit if requested
    if args.version:
        display_version()
        return 0
    
    # Set up environment
    env_setup_success = setup_environment(debug=args.debug, config_path=args.config)
    if not env_setup_success and args.config:
        logger.error(f"Failed to set up environment with config file: {args.config}")
        return 1
    
    # Print banner
    print("=" * 80)
    print(f"TaskWeaver v{__version__} - A code-first agent framework for data analytics tasks")
    print("=" * 80)
    
    # Validate CLI mode has project directory
    if args.cli and not args.project:
        logger.error("Project directory is required for CLI mode. Use --project to specify a project directory.")
        return 1
    
    # Launch the appropriate UI
    if args.web:
        return launch_web_ui(host=args.host, port=args.port, config_path=args.config, auto_install=args.auto_install)
    elif args.gui:
        return launch_gui(config_path=args.config, auto_install=args.auto_install)
    elif args.cli:
        return launch_cli(project_dir=args.project, interactive=args.interactive, 
                         config_path=args.config, auto_install=args.auto_install)
    else:
        # Default to web UI if no mode specified
        logger.info("No UI mode specified, defaulting to web UI")
        return launch_web_ui(host=args.host, port=args.port, config_path=args.config, auto_install=args.auto_install)

if __name__ == "__main__":
    sys.exit(main())
