#!/usr/bin/env python3
"""
TaskWeaver Main Entry Point
"""

import os
import sys
import argparse
import logging
from typing import Optional

from taskweaver import __version__

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("taskweaver")


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
    
    return parser.parse_args()


def display_version():
    """
    Display version information
    """
    print(f"TaskWeaver version: {__version__}")
    print("A code-first agent framework for data analytics tasks")
    print("https://github.com/microsoft/TaskWeaver")


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
    
    return True


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
    
    # Import the appropriate module based on the UI mode
    try:
        if args.web:
            from taskweaver.ui.server import run_server
            return run_server(host=args.host, port=args.port)
        elif args.gui:
            from taskweaver.ui.gui import run_gui
            return run_gui()
        elif args.cli:
            from taskweaver.cli import run_cli
            return run_cli(project_dir=args.project, interactive=args.interactive)
        else:
            # Default to web UI if no mode specified
            logger.info("No UI mode specified, defaulting to web UI")
            from taskweaver.ui.server import run_server
            return run_server(host=args.host, port=args.port)
    except ImportError as e:
        logger.error(f"Failed to import required module: {str(e)}")
        logger.error("Make sure all dependencies are installed: pip install -e .")
        return 1
    except Exception as e:
        logger.error(f"Error: {str(e)}")
        return 1


if __name__ == "__main__":
    sys.exit(main())

