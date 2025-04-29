#!/usr/bin/env python3
"""
Example usage of the standalone TaskWeaver module.
"""

import os
import sys

from standalone_taskweaver import AppConfigSource
from standalone_taskweaver.app.session_manager import SessionManager
from standalone_taskweaver.logging import TelemetryLogger
from standalone_taskweaver.module.tracing import Tracing
from standalone_taskweaver import TaskWeaverApp

def main():
    """Main function to demonstrate TaskWeaver usage."""
    # Set up API credentials (replace with your own)
    os.environ["OPENAI_API_KEY"] = "your-api-key"
    os.environ["OPENAI_API_BASE"] = "https://api.openai.com/v1"
    os.environ["OPENAI_MODEL"] = "gpt-4"
    
    # Get the current directory as the project directory
    project_dir = os.path.dirname(os.path.abspath(__file__))
    
    try:
        # Create configuration
        config_source = AppConfigSource()
        config_source.app_base_path = project_dir
        
        # Create required components
        session_manager = SessionManager(config_source)
        logger = TelemetryLogger(config_source)
        tracing = Tracing(config_source)
        
        # Initialize the app with all required components
        app = TaskWeaverApp(
            config=config_source,
            session_manager=session_manager,
            logger=logger,
            tracing=tracing
        )
        
        print("TaskWeaver initialized successfully.")
        
        # Create a session
        session = app.create_session(session_name="Example Session")
        print(f"Created session: {session.session_metadata.session_name}")
        
        # Example chat interaction
        while True:
            user_input = input("\nYou: ")
            if user_input.lower() in ["exit", "quit"]:
                break
            
            response = session.chat(user_input)
            print(f"\nTaskWeaver: {response}")
        
    except Exception as e:
        print(f"Error: {str(e)}")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())

