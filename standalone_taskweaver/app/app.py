#!/usr/bin/env python3
"""
Main application module for TaskWeaver.
"""

import os
import sys
import argparse
from typing import Dict, Any, Optional


class TaskWeaverApp:
    """
    Main application class for TaskWeaver.
    """

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize the TaskWeaver application.

        Args:
            config: Optional configuration dictionary.
        """
        self.config = config or {}
        self.initialized = False

    def initialize(self) -> None:
        """
        Initialize the application.
        """
        self.initialized = True

    def run(self) -> None:
        """
        Run the application.
        """
        if not self.initialized:
            self.initialize()
        
        print("TaskWeaver application is running.")


def create_app(config: Optional[Dict[str, Any]] = None) -> TaskWeaverApp:
    """
    Create and initialize a TaskWeaver application.

    Args:
        config: Optional configuration dictionary.

    Returns:
        An initialized TaskWeaver application.
    """
    app = TaskWeaverApp(config)
    app.initialize()
    return app


def main() -> None:
    """
    Main entry point for the TaskWeaver application.
    """
    parser = argparse.ArgumentParser(description="TaskWeaver: A code-first agent framework for data analytics tasks")
    parser.add_argument("--config", help="Path to configuration file")
    parser.add_argument("--port", help="Port to run the web server on")
    parser.add_argument("--host", help="Host to run the web server on")
    parser.add_argument("--debug", action="store_true", help="Run in debug mode")
    
    args = parser.parse_args()
    
    config = {}
    if args.config:
        # Load configuration from file
        config["config_path"] = args.config
    
    if args.port:
        config["port"] = args.port
    
    if args.host:
        config["host"] = args.host
    
    if args.debug:
        config["debug"] = True
    
    app = create_app(config)
    app.run()


if __name__ == "__main__":
    main()

