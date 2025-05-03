#!/usr/bin/env python3
"""
Enhanced main entry point for TaskWeaver UI with Codegen integration
"""

import os
import sys
import logging
import argparse

from standalone_taskweaver.app.app import TaskWeaverApp
from standalone_taskweaver.config.config_mgt import AppConfigSource
from standalone_taskweaver.logging import TelemetryLogger
from standalone_taskweaver.ui.server_enhanced import TaskWeaverServerEnhanced
from standalone_taskweaver.ui.taskweaver_ui_enhanced import TaskWeaverUIEnhanced

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("taskweaver-main-enhanced")

def main():
    """
    Main entry point for TaskWeaver UI with Codegen integration
    """
    parser = argparse.ArgumentParser(description="TaskWeaver UI with Codegen integration")
    parser.add_argument("--host", type=str, default="0.0.0.0", help="Host to run the server on")
    parser.add_argument("--port", type=int, default=5000, help="Port to run the server on")
    parser.add_argument("--config", type=str, default=None, help="Path to config file")
    
    args = parser.parse_args()
    
    # Create app
    app = TaskWeaverApp()
    
    # Create config
    config = AppConfigSource()
    
    if args.config:
        config.load_from_file(args.config)
    
    # Create logger
    logger = TelemetryLogger()
    
    # Create UI
    ui = TaskWeaverUIEnhanced(app, config, logger)
    
    # Create server
    server = TaskWeaverServerEnhanced(app, config, logger, ui, args.host, args.port)
    
    # Run server
    server.run()

if __name__ == "__main__":
    main()

