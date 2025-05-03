"""
Main entry point for the enhanced TaskWeaver UI
"""

import os
import sys
import argparse

from standalone_taskweaver.ui.server_enhanced import run_server

def main():
    """
    Main entry point for the enhanced TaskWeaver UI
    """
    parser = argparse.ArgumentParser(description="TaskWeaver UI with Codegen integration")
    parser.add_argument("--host", type=str, default="0.0.0.0", help="Host to run the server on")
    parser.add_argument("--port", type=int, default=8000, help="Port to run the server on")
    args = parser.parse_args()
    
    print(f"Starting TaskWeaver UI with Codegen integration on {args.host}:{args.port}")
    run_server(host=args.host, port=args.port)

if __name__ == "__main__":
    main()

