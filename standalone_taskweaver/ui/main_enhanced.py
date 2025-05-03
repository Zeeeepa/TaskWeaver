#!/usr/bin/env python3
"""
Main entry point for Enhanced TaskWeaver UI
"""

import os
import sys
import argparse
import logging
from typing import Dict, Optional

from standalone_taskweaver.ui.server_enhanced import run_server

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("taskweaver-ui-enhanced")

def parse_args():
    """
    Parse command line arguments
    """
    parser = argparse.ArgumentParser(description="Enhanced TaskWeaver UI")
    
    parser.add_argument("--host", default="0.0.0.0", help="Host to bind the server to")
    parser.add_argument("--port", type=int, default=8000, help="Port to bind the server to")
    
    return parser.parse_args()

def main():
    """
    Main entry point
    """
    print("=" * 80)
    print("Enhanced TaskWeaver UI with Codegen Integration")
    print("=" * 80)
    
    # Parse command line arguments
    args = parse_args()
    
    # Run the server
    try:
        print(f"Starting server on {args.host}:{args.port}")
        run_server(host=args.host, port=args.port)
    except KeyboardInterrupt:
        print("\nStopping server...")
    except Exception as e:
        print(f"Error: {str(e)}")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())

