#!/usr/bin/env python3
"""
Run script for TaskWeaver UI
"""

import os
import sys
import argparse
from standalone_taskweaver.ui.server import run_server

def main():
    """
    Main function
    """
    parser = argparse.ArgumentParser(description="Run TaskWeaver UI")
    parser.add_argument("--host", type=str, default="0.0.0.0", help="Host to run the server on")
    parser.add_argument("--port", type=int, default=8000, help="Port to run the server on")
    args = parser.parse_args()
    
    print(f"Starting TaskWeaver UI on http://{args.host}:{args.port}")
    print("Press Ctrl+C to stop the server")
    
    run_server(host=args.host, port=args.port)

if __name__ == "__main__":
    main()

