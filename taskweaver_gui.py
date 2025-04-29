#!/usr/bin/env python3
"""
TaskWeaver GUI

This script provides a GUI interface for TaskWeaver.
"""

import os
import sys
import json
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QTextEdit, QFileDialog, QComboBox,
    QSplitter, QTreeWidget, QTreeWidgetItem, QTabWidget,
    QDialog, QLineEdit, QFormLayout, QDialogButtonBox, QMessageBox
)
from PyQt5.QtCore import Qt, QThread, pyqtSignal

from standalone_taskweaver import AppConfigSource, TaskWeaverApp
from standalone_taskweaver.session.session import Session
from standalone_taskweaver.app.session_manager import SessionManager
from standalone_taskweaver.logging import TelemetryLogger
from standalone_taskweaver.module.tracing import Tracing


class SettingsDialog(QDialog):
    """Dialog for configuring TaskWeaver settings"""
    
    def __init__(self, parent=None, settings=None):
        super().__init__(parent)
        self.settings = settings or {}
        self.init_ui()
        
    def init_ui(self):
        """Initialize the UI components"""
        self.setWindowTitle("TaskWeaver Settings")
        self.setMinimumWidth(400)
        
        layout = QFormLayout(self)
        
        # API Endpoint
        self.api_endpoint = QLineEdit(self.settings.get("api_endpoint", "https://api.openai.com/v1"))
        layout.addRow("API Endpoint:", self.api_endpoint)
        
        # API Key
        self.api_key = QLineEdit(self.settings.get("api_key", ""))
        self.api_key.setEchoMode(QLineEdit.Password)
        layout.addRow("API Key:", self.api_key)
        
        # Model
        self.model = QLineEdit(self.settings.get("model", "gpt-4"))
        layout.addRow("Model:", self.model)
        
        # Buttons
        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        layout.addRow(button_box)
    
    def get_settings(self):
        """Get the settings from the dialog"""
        return {
            "api_endpoint": self.api_endpoint.text(),
            "api_key": self.api_key.text(),
            "model": self.model.text()
        }


class TaskWeaverWorker(QThread):
    """Worker thread for TaskWeaver operations"""
    response_signal = pyqtSignal(str)
    
    def __init__(self, session, message):
        super().__init__()
        self.session = session
        self.message = message
        
    def run(self):
        response = self.session.chat(self.message)
        self.response_signal.emit(response)


class TaskWeaverGUI(QMainWindow):
    """Main GUI window for TaskWeaver"""
    
    def __init__(self):
        super().__init__()
        self.app = None
        self.session = None
        self.project_dir = None
        self.settings = self.load_settings()
        self.init_ui()
        
    def init_ui(self):
        """Initialize the UI components"""
        self.setWindowTitle("TaskWeaver")
        self.setGeometry(100, 100, 1200, 800)
        
        # Main layout
        main_widget = QWidget()
        main_layout = QVBoxLayout()
        main_widget.setLayout(main_layout)
        self.setCentralWidget(main_widget)
        
        # Project selection
        project_layout = QHBoxLayout()
        project_label = QLabel("Project Directory:")
        self.project_path = QTextEdit()
        self.project_path.setMaximumHeight(30)
        self.project_path.setReadOnly(True)
        browse_button = QPushButton("Browse")
        browse_button.clicked.connect(self.browse_project)
        init_button = QPushButton("Initialize")
        init_button.clicked.connect(self.initialize_taskweaver)
        settings_button = QPushButton("Settings")
        settings_button.clicked.connect(self.open_settings)
        
        project_layout.addWidget(project_label)
        project_layout.addWidget(self.project_path)
        project_layout.addWidget(browse_button)
        project_layout.addWidget(init_button)
        project_layout.addWidget(settings_button)
        main_layout.addLayout(project_layout)
        
        # Main content splitter
        splitter = QSplitter(Qt.Horizontal)
        main_layout.addWidget(splitter, 1)
        
        # Left panel - Sessions and Plan View
        left_panel = QTabWidget()
        
        # Sessions tab
        sessions_widget = QWidget()
        sessions_layout = QVBoxLayout()
        sessions_widget.setLayout(sessions_layout)
        
        self.sessions_list = QTreeWidget()
        self.sessions_list.setHeaderLabels(["Sessions"])
        self.sessions_list.itemClicked.connect(self.session_selected)
        sessions_layout.addWidget(self.sessions_list)
        
        session_buttons = QHBoxLayout()
        new_session_button = QPushButton("New Session")
        new_session_button.clicked.connect(self.create_new_session)
        session_buttons.addWidget(new_session_button)
        sessions_layout.addLayout(session_buttons)
        
        left_panel.addTab(sessions_widget, "Sessions")
        
        # Plan View tab
        plan_widget = QWidget()
        plan_layout = QVBoxLayout()
        plan_widget.setLayout(plan_layout)
        
        self.plan_view = QTextEdit()
        self.plan_view.setReadOnly(True)
        plan_layout.addWidget(self.plan_view)
        
        left_panel.addTab(plan_widget, "Plan View")
        
        splitter.addWidget(left_panel)
        
        # Right panel - Chat Interface
        chat_widget = QWidget()
        chat_layout = QVBoxLayout()
        chat_widget.setLayout(chat_layout)
        
        self.chat_history = QTextEdit()
        self.chat_history.setReadOnly(True)
        chat_layout.addWidget(self.chat_history)
        
        input_layout = QHBoxLayout()
        self.chat_input = QTextEdit()
        self.chat_input.setMaximumHeight(60)
        send_button = QPushButton("Send")
        send_button.clicked.connect(self.send_message)
        
        input_layout.addWidget(self.chat_input)
        input_layout.addWidget(send_button)
        chat_layout.addLayout(input_layout)
        
        splitter.addWidget(chat_widget)
        
        # Set initial splitter sizes
        splitter.setSizes([300, 900])
    
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
        except Exception as e:
            self.chat_history.append(f"Error saving settings: {str(e)}")
    
    def open_settings(self):
        """Open the settings dialog"""
        dialog = SettingsDialog(self, self.settings)
        if dialog.exec_() == QDialog.Accepted:
            self.settings = dialog.get_settings()
            self.save_settings()
            self.chat_history.append("Settings updated. Please reinitialize TaskWeaver.")
    
    def browse_project(self):
        """Open file dialog to select project directory"""
        dir_path = QFileDialog.getExistingDirectory(self, "Select Project Directory")
        if dir_path:
            self.project_dir = dir_path
            self.project_path.setText(dir_path)
    
    def initialize_taskweaver(self):
        """Initialize TaskWeaver with the selected project directory"""
        if not self.project_dir:
            self.chat_history.append("Please select a project directory first.")
            return
        
        try:
            # Set environment variables for API
            os.environ["OPENAI_API_KEY"] = self.settings.get("api_key", "")
            os.environ["OPENAI_API_BASE"] = self.settings.get("api_endpoint", "https://api.openai.com/v1")
            os.environ["OPENAI_MODEL"] = self.settings.get("model", "gpt-4")
            
            # Create config with project directory
            config_source = AppConfigSource()
            config_source.app_base_path = self.project_dir
            
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
            
            self.chat_history.append("TaskWeaver initialized successfully.")
            self.update_sessions_list()
        except Exception as e:
            self.chat_history.append(f"Error initializing TaskWeaver: {str(e)}")
    
    def update_sessions_list(self):
        """Update the sessions list in the UI"""
        if not self.app:
            return
        
        self.sessions_list.clear()
        
        # Get actual sessions from the app
        sessions = self.app.list_sessions()
        if sessions:
            for session_id, session in sessions.items():
                item = QTreeWidgetItem([session.session_metadata.session_name or session_id])
                item.setData(0, Qt.UserRole, session_id)
                self.sessions_list.addTopLevelItem(item)
        else:
            # Add a placeholder if no sessions exist
            item = QTreeWidgetItem(["No sessions available"])
            self.sessions_list.addTopLevelItem(item)
    
    def session_selected(self, item):
        """Handle session selection from the list"""
        session_id = item.data(0, Qt.UserRole)
        if session_id and self.app:
            try:
                self.session = self.app.get_session(session_id)
                self.chat_history.append(f"\nSwitched to session: {self.session.session_metadata.session_name or session_id}")
                
                # Update chat history with session messages
                self.refresh_chat_history()
            except Exception as e:
                self.chat_history.append(f"Error selecting session: {str(e)}")
    
    def refresh_chat_history(self):
        """Refresh the chat history from the current session"""
        if not self.session:
            return
            
        # Clear current history
        self.chat_history.clear()
        
        # In a real implementation, you would get the actual chat history from the session
        # For now, we'll just add a placeholder
        self.chat_history.append("Session started. Type a message to begin.")
    
    def create_new_session(self):
        """Create a new TaskWeaver session"""
        if not self.app:
            self.chat_history.append("Please initialize TaskWeaver first.")
            return
        
        try:
            session_name = f"Session_{len(self.app.list_sessions()) + 1}"
            self.session = self.app.create_session(session_name=session_name)
            self.chat_history.append(f"Created new session: {session_name}")
            self.update_sessions_list()
            self.refresh_chat_history()
        except Exception as e:
            self.chat_history.append(f"Error creating session: {str(e)}")
    
    def send_message(self):
        """Send a message to the current TaskWeaver session"""
        if not self.session:
            self.chat_history.append("Please create a session first.")
            return
        
        message = self.chat_input.toPlainText()
        if not message:
            return
        
        self.chat_history.append(f"\nYou: {message}")
        self.chat_input.clear()
        
        # Process the message in a separate thread to keep the UI responsive
        self.worker = TaskWeaverWorker(self.session, message)
        self.worker.response_signal.connect(self.handle_response)
        self.worker.start()
    
    def handle_response(self, response):
        """Handle the response from TaskWeaver"""
        self.chat_history.append(f"\nTaskWeaver: {response}")
        
        # Update the plan view (in a real implementation, you would extract the plan from the session)
        # For now, we'll just add a placeholder
        self.plan_view.setText("Task Plan:\n1. Understand user request\n2. Break down into subtasks\n3. Execute each subtask\n4. Return results")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    gui = TaskWeaverGUI()
    gui.show()
    sys.exit(app.exec_())
