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
from typing import Dict, Optional, List, Any

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
    cli_group.add_argument("--project", type=str, help="Project directory path for CLI mode")
    cli_group.add_argument("--interactive", action="store_true", help="Run CLI in interactive mode")
    
    # Common options
    common_group = parser.add_argument_group("Common Options")
    common_group.add_argument("--config", type=str, help="Path to configuration file")
    common_group.add_argument("--debug", action="store_true", help="Enable debug logging")
    
    return parser.parse_args()

def launch_web_ui(host: str = "0.0.0.0", port: int = 8000):
    """
    Launch the web UI
    """
    try:
        from standalone_taskweaver.ui.server import run_server
        
        logger.info(f"Starting TaskWeaver Web UI on http://{host}:{port}")
        logger.info("Press Ctrl+C to stop the server")
        
        run_server(host=host, port=port)
        return 0
    except ImportError as e:
        logger.error(f"Failed to import web UI components: {str(e)}")
        logger.error("Make sure all dependencies are installed: pip install -e .")
        return 1
    except Exception as e:
        logger.error(f"Error launching web UI: {str(e)}")
        return 1

def launch_gui():
    """
    Launch the desktop GUI
    """
    try:
        from PyQt5.QtWidgets import QApplication
        from taskweaver_gui import TaskWeaverGUI
        
        logger.info("Starting TaskWeaver Desktop GUI")
        
        app = QApplication(sys.argv)
        gui = TaskWeaverGUI()
        gui.show()
        return app.exec_()
    except ImportError as e:
        logger.error(f"Failed to import GUI components: {str(e)}")
        logger.error("Make sure PyQt5 is installed: pip install PyQt5")
        return 1
    except Exception as e:
        logger.error(f"Error launching GUI: {str(e)}")
        return 1

def launch_cli(project_dir: Optional[str] = None, interactive: bool = False):
    """
    Launch the CLI interface
    """
    try:
        from taskweaver_launcher import TaskWeaverCLI
        
        logger.info("Starting TaskWeaver CLI")
        
        cli = TaskWeaverCLI()
        
        if interactive and project_dir:
            logger.info(f"Running in interactive mode with project directory: {project_dir}")
            cli.run_interactive(project_dir)
            return 0
        elif project_dir:
            # Initialize and return
            success = cli.initialize(project_dir)
            return 0 if success else 1
        else:
            logger.error("Project directory is required for CLI mode")
            logger.error("Use --project to specify a project directory")
            return 1
    except ImportError as e:
        logger.error(f"Failed to import CLI components: {str(e)}")
        logger.error("Make sure all dependencies are installed: pip install -e .")
        return 1
    except Exception as e:
        logger.error(f"Error launching CLI: {str(e)}")
        return 1

def setup_environment(debug: bool = False):
    """
    Set up the environment for TaskWeaver
    """
    # Set up logging level
    if debug:
        logging.getLogger().setLevel(logging.DEBUG)
        logger.debug("Debug logging enabled")
    
    # Check for required environment variables
    if not os.environ.get("OPENAI_API_KEY"):
        logger.warning("OPENAI_API_KEY environment variable not set")
        logger.warning("You may need to set this for TaskWeaver to function properly")

def main():
    """
    Main entry point
    """
    # Parse command line arguments
    args = parse_args()
    
    # Set up environment
    setup_environment(debug=args.debug)
    
    # Print banner
    print("=" * 80)
    print("TaskWeaver - A code-first agent framework for data analytics tasks")
    print("=" * 80)
    
    # Launch the appropriate UI
    if args.web:
        return launch_web_ui(host=args.host, port=args.port)
    elif args.gui:
        return launch_gui()
    elif args.cli:
        return launch_cli(project_dir=args.project, interactive=args.interactive)
    else:
        # Default to web UI if no mode specified
        logger.info("No UI mode specified, defaulting to web UI")
        return launch_web_ui(host=args.host, port=args.port)

if __name__ == "__main__":
    sys.exit(main())

