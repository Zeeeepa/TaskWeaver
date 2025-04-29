#!/usr/bin/env python3
"""
TaskWeaver Launcher

This script provides a launcher for TaskWeaver with both CLI and GUI modes.
"""

import os
import sys
import argparse
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QTextEdit, QFileDialog, QComboBox,
    QSplitter, QTreeWidget, QTreeWidgetItem, QTabWidget
)
from PyQt5.QtCore import Qt, QThread, pyqtSignal

from standalone_taskweaver import TaskWeaverApp, AppConfigSource, Session


class TaskWeaverWorker(QThread):
    """Worker thread for TaskWeaver operations"""
    response_signal = pyqtSignal(str)
    
    def __init__(self, app, session, message):
        super().__init__()
        self.app = app
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
        
        project_layout.addWidget(project_label)
        project_layout.addWidget(self.project_path)
        project_layout.addWidget(browse_button)
        project_layout.addWidget(init_button)
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
            config_source = AppConfigSource()
            self.app = TaskWeaverApp(config_source)
            self.chat_history.append("TaskWeaver initialized successfully.")
            self.update_sessions_list()
        except Exception as e:
            self.chat_history.append(f"Error initializing TaskWeaver: {str(e)}")
    
    def update_sessions_list(self):
        """Update the sessions list in the UI"""
        if not self.app:
            return
        
        self.sessions_list.clear()
        # In a real implementation, you would get the actual sessions from the app
        # For now, we'll just add a placeholder
        item = QTreeWidgetItem(["Default Session"])
        self.sessions_list.addTopLevelItem(item)
    
    def create_new_session(self):
        """Create a new TaskWeaver session"""
        if not self.app:
            self.chat_history.append("Please initialize TaskWeaver first.")
            return
        
        try:
            session_name = f"Session_{len(self.sessions_list.findItems('', Qt.MatchContains))}"
            self.session = self.app.create_session(session_name)
            self.chat_history.append(f"Created new session: {session_name}")
            self.update_sessions_list()
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
        self.worker = TaskWeaverWorker(self.app, self.session, message)
        self.worker.response_signal.connect(self.handle_response)
        self.worker.start()
    
    def handle_response(self, response):
        """Handle the response from TaskWeaver"""
        self.chat_history.append(f"\nTaskWeaver: {response}")
        
        # Update the plan view (in a real implementation, you would extract the plan from the session)
        self.plan_view.setText("Task Plan:\n1. Understand user request\n2. Break down into subtasks\n3. Execute each subtask\n4. Return results")


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description="TaskWeaver Launcher")
    parser.add_argument("--cli", action="store_true", help="Run in CLI mode")
    args = parser.parse_args()
    
    if args.cli:
        # CLI mode
        print("TaskWeaver CLI mode")
        # Implement CLI mode here
    else:
        # GUI mode
        app = QApplication(sys.argv)
        gui = TaskWeaverGUI()
        gui.show()
        sys.exit(app.exec_())


if __name__ == "__main__":
    main()

