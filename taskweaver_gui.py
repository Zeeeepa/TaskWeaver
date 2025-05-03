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
    QDialog, QLineEdit, QFormLayout, QDialogButtonBox, QMessageBox,
    QProgressBar, QStatusBar
)
from PyQt5.QtCore import Qt, QThread, pyqtSignal
from PyQt5.QtGui import QIcon, QFont, QTextCursor

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
        self.setMinimumWidth(500)
        
        layout = QFormLayout(self)
        
        # API Endpoint
        self.api_endpoint = QLineEdit(self.settings.get("api_endpoint", "https://api.openai.com/v1"))
        layout.addRow("API Endpoint:", self.api_endpoint)
        
        # API Key
        self.api_key = QLineEdit(self.settings.get("api_key", ""))
        self.api_key.setEchoMode(QLineEdit.Password)
        layout.addRow("API Key:", self.api_key)
        
        # Model
        self.model = QComboBox()
        models = ["gpt-4", "gpt-4-turbo", "gpt-4o", "gpt-3.5-turbo"]
        current_model = self.settings.get("model", "gpt-4")
        
        for model in models:
            self.model.addItem(model)
        
        # Set current model if it exists in the list, otherwise add it
        index = self.model.findText(current_model)
        if index >= 0:
            self.model.setCurrentIndex(index)
        else:
            self.model.addItem(current_model)
            self.model.setCurrentIndex(self.model.count() - 1)
        
        layout.addRow("Model:", self.model)
        
        # Custom model input
        self.custom_model = QLineEdit()
        self.custom_model.setPlaceholderText("Enter custom model name")
        layout.addRow("Custom Model:", self.custom_model)
        
        # Add custom model button
        add_model_button = QPushButton("Add Custom Model")
        add_model_button.clicked.connect(self.add_custom_model)
        layout.addRow("", add_model_button)
        
        # Buttons
        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        layout.addRow(button_box)
    
    def add_custom_model(self):
        """Add a custom model to the dropdown"""
        custom_model = self.custom_model.text().strip()
        if custom_model:
            # Check if model already exists
            index = self.model.findText(custom_model)
            if index < 0:
                self.model.addItem(custom_model)
                self.model.setCurrentIndex(self.model.count() - 1)
            else:
                self.model.setCurrentIndex(index)
            
            self.custom_model.clear()
    
    def get_settings(self):
        """Get the settings from the dialog"""
        return {
            "api_endpoint": self.api_endpoint.text(),
            "api_key": self.api_key.text(),
            "model": self.model.currentText()
        }


class TaskWeaverWorker(QThread):
    """Worker thread for TaskWeaver operations"""
    response_signal = pyqtSignal(str)
    error_signal = pyqtSignal(str)
    progress_signal = pyqtSignal(int)
    
    def __init__(self, session, message):
        super().__init__()
        self.session = session
        self.message = message
        
    def run(self):
        try:
            self.progress_signal.emit(10)  # Start progress
            response = self.session.chat(self.message)
            self.progress_signal.emit(100)  # Complete progress
            self.response_signal.emit(response)
        except Exception as e:
            self.error_signal.emit(str(e))
            self.progress_signal.emit(0)  # Reset progress


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
        delete_session_button = QPushButton("Delete Session")
        delete_session_button.clicked.connect(self.delete_session)
        session_buttons.addWidget(new_session_button)
        session_buttons.addWidget(delete_session_button)
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
        
        # Settings tab
        settings_widget = QWidget()
        settings_layout = QVBoxLayout()
        settings_widget.setLayout(settings_layout)
        
        # Display current settings
        self.settings_view = QTextEdit()
        self.settings_view.setReadOnly(True)
        settings_layout.addWidget(self.settings_view)
        
        # Update settings display
        self.update_settings_display()
        
        left_panel.addTab(settings_widget, "Settings")
        
        splitter.addWidget(left_panel)
        
        # Right panel - Chat Interface
        chat_widget = QWidget()
        chat_layout = QVBoxLayout()
        chat_widget.setLayout(chat_layout)
        
        self.chat_history = QTextEdit()
        self.chat_history.setReadOnly(True)
        chat_layout.addWidget(self.chat_history)
        
        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        self.progress_bar.setVisible(False)
        chat_layout.addWidget(self.progress_bar)
        
        input_layout = QHBoxLayout()
        self.chat_input = QTextEdit()
        self.chat_input.setMaximumHeight(60)
        self.chat_input.setPlaceholderText("Type your message here...")
        
        # Enable sending message with Ctrl+Enter
        self.chat_input.installEventFilter(self)
        
        send_button = QPushButton("Send")
        send_button.clicked.connect(self.send_message)
        
        input_layout.addWidget(self.chat_input)
        input_layout.addWidget(send_button)
        chat_layout.addLayout(input_layout)
        
        splitter.addWidget(chat_widget)
        
        # Set initial splitter sizes
        splitter.setSizes([300, 900])
        
        # Status bar
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("Ready")
    
    def eventFilter(self, obj, event):
        """Handle events for objects with event filters"""
        if obj is self.chat_input and event.type() == event.KeyPress:
            if event.key() == Qt.Key_Return and event.modifiers() == Qt.ControlModifier:
                self.send_message()
                return True
        return super().eventFilter(obj, event)
    
    def update_settings_display(self):
        """Update the settings display in the settings tab"""
        if hasattr(self, 'settings_view'):
            settings_text = "Current Settings:\n\n"
            settings_text += f"API Endpoint: {self.settings.get('api_endpoint', 'Not set')}\n"
            settings_text += f"API Key: {'*' * 10 if self.settings.get('api_key') else 'Not set'}\n"
            settings_text += f"Model: {self.settings.get('model', 'Not set')}\n"
            
            if self.project_dir:
                settings_text += f"\nProject Directory: {self.project_dir}\n"
            
            self.settings_view.setText(settings_text)
    
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
            self.update_settings_display()
        except Exception as e:
            self.show_error(f"Error saving settings: {str(e)}")
    
    def open_settings(self):
        """Open the settings dialog"""
        dialog = SettingsDialog(self, self.settings)
        if dialog.exec_() == QDialog.Accepted:
            self.settings = dialog.get_settings()
            self.save_settings()
            self.chat_history.append("Settings updated. Please reinitialize TaskWeaver.")
            self.status_bar.showMessage("Settings updated", 3000)
    
    def browse_project(self):
        """Open file dialog to select project directory"""
        dir_path = QFileDialog.getExistingDirectory(self, "Select Project Directory")
        if dir_path:
            self.project_dir = dir_path
            self.project_path.setText(dir_path)
            self.update_settings_display()
    
    def initialize_taskweaver(self):
        """Initialize TaskWeaver with the selected project directory"""
        if not self.project_dir:
            self.show_error("Please select a project directory first.")
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
            self.status_bar.showMessage("TaskWeaver initialized", 3000)
            self.update_sessions_list()
        except Exception as e:
            self.show_error(f"Error initializing TaskWeaver: {str(e)}")
    
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
                self.status_bar.showMessage(f"Session: {self.session.session_metadata.session_name or session_id}", 3000)
                
                # Update chat history with session messages
                self.refresh_chat_history()
            except Exception as e:
                self.show_error(f"Error selecting session: {str(e)}")
    
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
            self.show_error("Please initialize TaskWeaver first.")
            return
        
        try:
            session_name = f"Session_{len(self.app.list_sessions()) + 1}"
            self.session = self.app.create_session(session_name=session_name)
            self.chat_history.append(f"Created new session: {session_name}")
            self.status_bar.showMessage(f"Created session: {session_name}", 3000)
            self.update_sessions_list()
            self.refresh_chat_history()
        except Exception as e:
            self.show_error(f"Error creating session: {str(e)}")
    
    def delete_session(self):
        """Delete the selected session"""
        if not self.app:
            self.show_error("Please initialize TaskWeaver first.")
            return
        
        selected_items = self.sessions_list.selectedItems()
        if not selected_items:
            self.show_error("Please select a session to delete.")
            return
        
        session_id = selected_items[0].data(0, Qt.UserRole)
        if not session_id:
            return
        
        confirm = QMessageBox.question(
            self, 
            "Confirm Delete", 
            f"Are you sure you want to delete this session?",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if confirm == QMessageBox.Yes:
            try:
                # In a real implementation, you would call the app to delete the session
                # For now, we'll just update the UI
                self.chat_history.append(f"Deleted session: {session_id}")
                self.status_bar.showMessage(f"Deleted session: {session_id}", 3000)
                
                # Reset current session if it's the one being deleted
                if self.session and self.session.session_id == session_id:
                    self.session = None
                    self.chat_history.clear()
                
                self.update_sessions_list()
            except Exception as e:
                self.show_error(f"Error deleting session: {str(e)}")
    
    def send_message(self):
        """Send a message to the current TaskWeaver session"""
        if not self.session:
            self.show_error("Please create a session first.")
            return
        
        message = self.chat_input.toPlainText()
        if not message:
            return
        
        self.chat_history.append(f"\nYou: {message}")
        self.chat_input.clear()
        
        # Show progress bar
        self.progress_bar.setValue(0)
        self.progress_bar.setVisible(True)
        self.status_bar.showMessage("Processing...", 0)
        
        # Process the message in a separate thread to keep the UI responsive
        self.worker = TaskWeaverWorker(self.session, message)
        self.worker.response_signal.connect(self.handle_response)
        self.worker.error_signal.connect(self.handle_error)
        self.worker.progress_signal.connect(self.update_progress)
        self.worker.start()
    
    def update_progress(self, value):
        """Update the progress bar"""
        self.progress_bar.setValue(value)
        if value == 100:
            # Hide progress bar after a short delay
            self.progress_bar.setVisible(False)
            self.status_bar.showMessage("Ready", 3000)
    
    def handle_response(self, response):
        """Handle the response from TaskWeaver"""
        self.chat_history.append(f"\nTaskWeaver: {response}")
        
        # Scroll to the bottom
        self.chat_history.moveCursor(QTextCursor.End)
        
        # Update the plan view (in a real implementation, you would extract the plan from the session)
        # For now, we'll just add a placeholder
        self.plan_view.setText("Task Plan:\n1. Understand user request\n2. Break down into subtasks\n3. Execute each subtask\n4. Return results")
    
    def handle_error(self, error_message):
        """Handle errors from the worker thread"""
        self.show_error(f"Error processing message: {error_message}")
    
    def show_error(self, message):
        """Show an error message in the chat history and as a popup"""
        self.chat_history.append(f"\nError: {message}")
        self.status_bar.showMessage(f"Error: {message}", 5000)
        QMessageBox.critical(self, "Error", message)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    gui = TaskWeaverGUI()
    gui.show()
    sys.exit(app.exec_())
