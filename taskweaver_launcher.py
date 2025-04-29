#!/usr/bin/env python3
"""
TaskWeaver Launcher

This script provides a launcher for TaskWeaver with both CLI and GUI modes.
"""

import os
import sys
import json
import argparse
from PyQt5.QtWidgets import QApplication

# Import our GUI implementation
from taskweaver_gui import TaskWeaverGUI

# Import TaskWeaver components for CLI mode
from standalone_taskweaver import AppConfigSource, TaskWeaverApp
from standalone_taskweaver.app.session_manager import SessionManager
from standalone_taskweaver.logging import TelemetryLogger
from standalone_taskweaver.module.tracing import Tracing


class TaskWeaverCLI:
    """CLI interface for TaskWeaver"""
    
    def __init__(self):
        self.app = None
        self.session = None
        self.settings = self.load_settings()
    
    def load_settings(self):
        """Load settings from file"""
        settings_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "settings.json")
        if os.path.exists(settings_path):
            try:
                with open(settings_path, "r") as f:
                    return json.load(f)
            except Exception:
                pass
        return {
            "api_endpoint": "https://api.openai.com/v1",
            "api_key": "",
            "model": "gpt-4"
        }
    
    def initialize(self, project_dir):
        """Initialize TaskWeaver with the specified project directory"""
        try:
            # Set environment variables for API
            os.environ["OPENAI_API_KEY"] = self.settings.get("api_key", "")
            os.environ["OPENAI_API_BASE"] = self.settings.get("api_endpoint", "https://api.openai.com/v1")
            os.environ["OPENAI_MODEL"] = self.settings.get("model", "gpt-4")
            
            # Create config with project directory
            config_source = AppConfigSource()
            config_source.app_base_path = project_dir
            
            # Create required components
            session_manager = SessionManager(config_source)
            logger = TelemetryLogger(config_source)
            tracing = Tracing(config_source)
            
            # Initialize the app with all required components
            self.app = TaskWeaverApp(
                config=config_source,
                session_manager=session_manager,
                logger=logger,
                tracing=tracing
            )
            
            print("TaskWeaver initialized successfully.")
            return True
        except Exception as e:
            print(f"Error initializing TaskWeaver: {str(e)}")
            return False
    
    def create_session(self, session_name=None):
        """Create a new TaskWeaver session"""
        if not self.app:
            print("Please initialize TaskWeaver first.")
            return False
        
        try:
            if not session_name:
                session_name = f"Session_{len(self.app.list_sessions()) + 1}"
            
            self.session = self.app.create_session(session_name=session_name)
            print(f"Created new session: {session_name}")
            return True
        except Exception as e:
            print(f"Error creating session: {str(e)}")
            return False
    
    def chat(self, message):
        """Send a message to the current TaskWeaver session"""
        if not self.session:
            print("Please create a session first.")
            return None
        
        try:
            print(f"\nYou: {message}")
            response = self.session.chat(message)
            print(f"\nTaskWeaver: {response}")
            return response
        except Exception as e:
            print(f"Error sending message: {str(e)}")
            return None
    
    def run_interactive(self, project_dir):
        """Run TaskWeaver in interactive CLI mode"""
        if not self.initialize(project_dir):
            return
        
        if not self.create_session():
            return
        
        print("\nTaskWeaver CLI Interactive Mode")
        print("Type 'exit' or 'quit' to end the session")
        
        while True:
            try:
                message = input("\nYou: ")
                if message.lower() in ["exit", "quit"]:
                    break
                
                self.chat(message)
            except KeyboardInterrupt:
                break
            except Exception as e:
                print(f"Error: {str(e)}")
                break
        
        print("\nExiting TaskWeaver CLI")


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description="TaskWeaver Launcher")
    parser.add_argument("--cli", action="store_true", help="Run in CLI mode")
    parser.add_argument("--project", type=str, help="Project directory path")
    args = parser.parse_args()
    
    if args.cli:
        # CLI mode
        print("TaskWeaver CLI mode")
        cli = TaskWeaverCLI()
        
        if args.project:
            cli.run_interactive(args.project)
        else:
            print("Please specify a project directory with --project")
    else:
        # GUI mode
        app = QApplication(sys.argv)
        gui = TaskWeaverGUI()
        gui.show()
        sys.exit(app.exec_())


if __name__ == "__main__":
    main()

