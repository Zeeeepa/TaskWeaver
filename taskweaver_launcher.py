#!/usr/bin/env python3
"""
TaskWeaver Launcher

This script provides a launcher for TaskWeaver with both CLI and GUI modes.
"""

import os
import sys
import json
import argparse
import readline
import logging
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
        self.history = []
        self.setup_readline()
    
    def setup_readline(self):
        """Set up readline for command history"""
        # Set up command history
        history_file = os.path.join(os.path.expanduser("~"), ".taskweaver_history")
        try:
            readline.read_history_file(history_file)
            readline.set_history_length(1000)
        except FileNotFoundError:
            pass
        
        # Save history on exit
        import atexit
        atexit.register(readline.write_history_file, history_file)
    
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
    
    def save_settings(self):
        """Save settings to file"""
        settings_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "settings.json")
        try:
            with open(settings_path, "w") as f:
                json.dump(self.settings, f)
            return True
        except Exception as e:
            print(f"Error saving settings: {str(e)}")
            return False
    
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
    
    def list_sessions(self):
        """List all available sessions"""
        if not self.app:
            print("Please initialize TaskWeaver first.")
            return False
        
        try:
            sessions = self.app.list_sessions()
            if sessions:
                print("\nAvailable Sessions:")
                for i, (session_id, session) in enumerate(sessions.items(), 1):
                    print(f"{i}. {session.session_metadata.session_name or session_id}")
                return True
            else:
                print("No sessions available.")
                return False
        except Exception as e:
            print(f"Error listing sessions: {str(e)}")
            return False
    
    def select_session(self, session_index=None):
        """Select a session by index"""
        if not self.app:
            print("Please initialize TaskWeaver first.")
            return False
        
        try:
            sessions = list(self.app.list_sessions().items())
            if not sessions:
                print("No sessions available.")
                return False
            
            if session_index is None:
                self.list_sessions()
                try:
                    session_index = int(input("\nEnter session number to select: "))
                except ValueError:
                    print("Invalid input. Please enter a number.")
                    return False
            
            if 1 <= session_index <= len(sessions):
                session_id, _ = sessions[session_index - 1]
                self.session = self.app.get_session(session_id)
                print(f"Selected session: {self.session.session_metadata.session_name or session_id}")
                return True
            else:
                print(f"Invalid session number. Please enter a number between 1 and {len(sessions)}.")
                return False
        except Exception as e:
            print(f"Error selecting session: {str(e)}")
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
            self.history.append({"role": "user", "content": message})
            self.history.append({"role": "assistant", "content": response})
            return response
        except Exception as e:
            print(f"Error sending message: {str(e)}")
            return None
    
    def show_settings(self):
        """Display current settings"""
        print("\nCurrent Settings:")
        print(f"API Endpoint: {self.settings.get('api_endpoint', 'Not set')}")
        print(f"API Key: {'*' * 10 if self.settings.get('api_key') else 'Not set'}")
        print(f"Model: {self.settings.get('model', 'Not set')}")
    
    def update_settings(self):
        """Update settings interactively"""
        print("\nUpdate Settings:")
        
        # API Endpoint
        current_endpoint = self.settings.get("api_endpoint", "https://api.openai.com/v1")
        new_endpoint = input(f"API Endpoint [{current_endpoint}]: ")
        if new_endpoint:
            self.settings["api_endpoint"] = new_endpoint
        
        # API Key
        current_key = self.settings.get("api_key", "")
        masked_key = "*" * 10 if current_key else "Not set"
        new_key = input(f"API Key [{masked_key}]: ")
        if new_key:
            self.settings["api_key"] = new_key
        
        # Model
        current_model = self.settings.get("model", "gpt-4")
        print("\nAvailable models:")
        models = ["gpt-4", "gpt-4-turbo", "gpt-4o", "gpt-3.5-turbo"]
        for i, model in enumerate(models, 1):
            print(f"{i}. {model}")
        print(f"Current model: {current_model}")
        
        model_choice = input("Select model (number) or enter custom model name: ")
        if model_choice:
            try:
                index = int(model_choice) - 1
                if 0 <= index < len(models):
                    self.settings["model"] = models[index]
                else:
                    print("Invalid selection. Using custom input as model name.")
                    self.settings["model"] = model_choice
            except ValueError:
                # Not a number, use as custom model name
                self.settings["model"] = model_choice
        
        # Save settings
        if self.save_settings():
            print("Settings updated successfully.")
        else:
            print("Failed to save settings.")
    
    def show_help(self):
        """Display help information"""
        print("\nTaskWeaver CLI Commands:")
        print("  /help              - Show this help message")
        print("  /settings          - Show current settings")
        print("  /update_settings   - Update settings")
        print("  /list_sessions     - List available sessions")
        print("  /select_session    - Select a session")
        print("  /new_session       - Create a new session")
        print("  /clear             - Clear the screen")
        print("  /exit or /quit     - Exit the CLI")
        print("\nType any other message to chat with TaskWeaver.")
    
    def clear_screen(self):
        """Clear the terminal screen"""
        os.system('cls' if os.name == 'nt' else 'clear')
    
    def run_interactive(self, project_dir):
        """Run TaskWeaver in interactive CLI mode"""
        if not self.initialize(project_dir):
            return
        
        # Create a session if none exists
        sessions = self.app.list_sessions()
        if not sessions:
            if not self.create_session():
                return
        else:
            # Select the first session
            self.select_session(1)
        
        print("\nTaskWeaver CLI Interactive Mode")
        print("Type '/help' for a list of commands")
        
        while True:
            try:
                message = input("\nYou: ")
                
                # Handle commands
                if message.lower() in ["/exit", "/quit"]:
                    break
                elif message.lower() == "/help":
                    self.show_help()
                elif message.lower() == "/settings":
                    self.show_settings()
                elif message.lower() == "/update_settings":
                    self.update_settings()
                elif message.lower() == "/list_sessions":
                    self.list_sessions()
                elif message.lower() == "/select_session":
                    self.select_session()
                elif message.lower() == "/new_session":
                    self.create_session()
                elif message.lower() == "/clear":
                    self.clear_screen()
                else:
                    # Regular chat message
                    self.chat(message)
            except KeyboardInterrupt:
                print("\nOperation interrupted. Type '/exit' to quit.")
            except EOFError:
                break
            except Exception as e:
                print(f"Error: {str(e)}")
        
        print("\nExiting TaskWeaver CLI")


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description="TaskWeaver Launcher")
    parser.add_argument("--cli", action="store_true", help="Run in CLI mode")
    parser.add_argument("--gui", action="store_true", help="Run in GUI mode")
    parser.add_argument("--project", type=str, help="Project directory path")
    parser.add_argument("--model", type=str, help="Override the model to use (e.g., gpt-4-turbo, gpt-4o)")
    parser.add_argument("--debug", action="store_true", help="Enable debug logging")
    args = parser.parse_args()
    
    # Set up logging
    log_level = logging.DEBUG if args.debug else logging.INFO
    logging.basicConfig(
        level=log_level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Override model if provided
    if args.model:
        os.environ["OPENAI_MODEL"] = args.model
        print(f"Using model: {args.model}")
    
    if args.cli:
        # CLI mode
        print("TaskWeaver CLI mode")
        cli = TaskWeaverCLI()
        
        if args.project:
            cli.run_interactive(args.project)
        else:
            print("Please specify a project directory with --project")
    elif args.gui:
        # GUI mode
        app = QApplication(sys.argv)
        gui = TaskWeaverGUI()
        gui.show()
        sys.exit(app.exec_())
    else:
        # Default to GUI mode
        app = QApplication(sys.argv)
        gui = TaskWeaverGUI()
        gui.show()
        sys.exit(app.exec_())


if __name__ == "__main__":
    main()
