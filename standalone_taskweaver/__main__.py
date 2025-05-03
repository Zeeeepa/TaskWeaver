#!/usr/bin/env python3
import sys
import os
import argparse

def main():
    """
    Main entry point for the TaskWeaver application.
    """
    # Import here to avoid circular imports
    from standalone_taskweaver.app import app
    
    parser = argparse.ArgumentParser(description="TaskWeaver: A code-first agent framework for data analytics tasks")
    parser.add_argument("--config", type=str, help="Path to configuration file")
    parser.add_argument("--port", type=int, default=8080, help="Port to run the web server on")
    parser.add_argument("--host", type=str, default="127.0.0.1", help="Host to run the web server on")
    parser.add_argument("--debug", action="store_true", help="Run in debug mode")
    
    args = parser.parse_args()
    
    # Start the application
    app.run(host=args.host, port=args.port, debug=args.debug, config_path=args.config)

if __name__ == "__main__":
    main()

