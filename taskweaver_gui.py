#!/usr/bin/env python3
"""
TaskWeaver GUI - A graphical interface for TaskWeaver
"""

import os
import sys
from typing import Dict, List, Optional, Tuple

from PyQt5.QtCore import Qt, QThread, pyqtSignal
from PyQt5.QtGui import QFont, QIcon, QTextCursor
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QTextEdit, QLineEdit, QLabel, QSplitter,
    QTreeView, QFileSystemModel, QTabWidget, QFileDialog,
    QMessageBox, QListWidget, QListWidgetItem, QFrame
)

from standalone_taskweaver import AppConfigSource, TaskWeaverApp, Session
from standalone_taskweaver.logging import TelemetryLogger
from standalone_taskweaver.module.tracing import Tracing


class ChatWorker(QThread):
    """Worker thread for handling chat interactions"""
    response_received = pyqtSignal(str)
    error_occurred = pyqtSignal(str)

    def __init__(self, session: Session, message: str):
        super().__init__()
        self.session = session
        self.message = message

    def run(self):
        try:
            response = self.session.chat(self.message)
            self.response_received.emit(response)
        except Exception as e:
            self.error_occurred.emit(str(e))


class TaskWeaverGUI(QMainWindow):
    """Main GUI window for TaskWeaver"""

    def __init__(self):
        super().__init__()
        self.app_config = None
        self.taskweaver_app = None
        self.current_session = None
        self.current_project_path = None
        self.sessions = {}
        
        self.init_ui()
        
    def init_ui(self):
        """Initialize the user interface"""
        self.setWindowTitle("TaskWeaver GUI")
        self.setGeometry(100, 100, 1200, 800)
        
        # Main layout
        main_widget = QWidget()
        main_layout = QHBoxLayout(main_widget)
        self.setCentralWidget(main_widget)
        
        # Left panel for project selection and sessions
        left_panel = QWidget()
        left_layout = QVBoxLayout(left_panel)
        
        # Project selection
        project_group = QFrame()
        project_group.setFrameShape(QFrame.StyledPanel)
        project_layout = QVBoxLayout(project_group)
        
        project_header = QLabel("Project")
        project_header.setFont(QFont("Arial", 12, QFont.Bold))
        project_layout.addWidget(project_header)
        
        project_path_layout = QHBoxLayout()
        self.project_path_edit = QLineEdit()
        self.project_path_edit.setReadOnly(True)
        project_path_layout.addWidget(self.project_path_edit)
        
        browse_button = QPushButton("Browse")
        browse_button.clicked.connect(self.browse_project)
        project_path_layout.addWidget(browse_button)
        
        project_layout.addLayout(project_path_layout)
        
        # Initialize project button
        init_project_button = QPushButton("Initialize TaskWeaver")
        init_project_button.clicked.connect(self.initialize_taskweaver)
        project_layout.addWidget(init_project_button)
        
        left_layout.addWidget(project_group)
        
        # Sessions list
        sessions_group = QFrame()
        sessions_group.setFrameShape(QFrame.StyledPanel)
        sessions_layout = QVBoxLayout(sessions_group)
        
        sessions_header = QLabel("Sessions")
        sessions_header.setFont(QFont("Arial", 12, QFont.Bold))
        sessions_layout.addWidget(sessions_header)
        
        self.sessions_list = QListWidget()
        self.sessions_list.itemClicked.connect(self.select_session)
        sessions_layout.addWidget(self.sessions_list)
        
        sessions_buttons_layout = QHBoxLayout()
        new_session_button = QPushButton("New Session")
        new_session_button.clicked.connect(self.create_new_session)
        sessions_buttons_layout.addWidget(new_session_button)
        
        delete_session_button = QPushButton("Delete Session")
        delete_session_button.clicked.connect(self.delete_session)
        sessions_buttons_layout.addWidget(delete_session_button)
        
        sessions_layout.addLayout(sessions_buttons_layout)
        
        left_layout.addWidget(sessions_group)
        
        # Right panel with tabs
        right_panel = QTabWidget()
        
        # Chat tab
        chat_widget = QWidget()
        chat_layout = QVBoxLayout(chat_widget)
        
        self.chat_history = QTextEdit()
        self.chat_history.setReadOnly(True)
        chat_layout.addWidget(self.chat_history)
        
        chat_input_layout = QHBoxLayout()
        self.chat_input = QLineEdit()
        self.chat_input.returnPressed.connect(self.send_message)
        chat_input_layout.addWidget(self.chat_input)
        
        send_button = QPushButton("Send")
        send_button.clicked.connect(self.send_message)
        chat_input_layout.addWidget(send_button)
        
        chat_layout.addLayout(chat_input_layout)
        
        right_panel.addTab(chat_widget, "Chat")
        
        # Plan view tab
        plan_widget = QWidget()
        plan_layout = QVBoxLayout(plan_widget)
        
        self.plan_view = QTextEdit()
        self.plan_view.setReadOnly(True)
        plan_layout.addWidget(self.plan_view)
        
        right_panel.addTab(plan_widget, "Plan")
        
        # Project explorer tab
        explorer_widget = QWidget()
        explorer_layout = QVBoxLayout(explorer_widget)
        
        self.file_model = QFileSystemModel()
        self.file_model.setRootPath("")
        
        self.tree_view = QTreeView()
        self.tree_view.setModel(self.file_model)
        self.tree_view.setColumnWidth(0, 250)
        explorer_layout.addWidget(self.tree_view)
        
        right_panel.addTab(explorer_widget, "Project Explorer")
        
        # Add panels to splitter
        splitter = QSplitter(Qt.Horizontal)
        splitter.addWidget(left_panel)
        splitter.addWidget(right_panel)
        splitter.setSizes([300, 900])
        
        main_layout.addWidget(splitter)
        
        # Disable UI elements until project is initialized
        self.set_ui_enabled(False)
        
        self.show()
    
    def set_ui_enabled(self, enabled: bool):
        """Enable or disable UI elements based on project initialization"""
        self.sessions_list.setEnabled(enabled)
        self.chat_input.setEnabled(enabled)
        self.chat_history.setEnabled(enabled)
        self.plan_view.setEnabled(enabled)
        
    def browse_project(self):
        """Open file dialog to select project folder"""
        folder = QFileDialog.getExistingDirectory(self, "Select Project Folder")
        if folder:
            self.project_path_edit.setText(folder)
            self.current_project_path = folder
            self.tree_view.setRootIndex(self.file_model.index(folder))
    
    def initialize_taskweaver(self):
        """Initialize TaskWeaver with the selected project folder"""
        if not self.current_project_path:
            QMessageBox.warning(self, "Warning", "Please select a project folder first.")
            return
        
        try:
            # Create the app config
            self.app_config = AppConfigSource(
                app_base_path=self.current_project_path,
            )
            
            # Create the logger
            logger = TelemetryLogger(
                log_dir=os.path.join(self.app_config.app_base_path, "logs"),
            )
            
            # Create the tracing
            tracing = Tracing()
            
            # Create the app
            self.taskweaver_app = TaskWeaverApp(
                config=self.app_config,
                logger=logger,
                tracing=tracing,
            )
            
            # Enable UI elements
            self.set_ui_enabled(True)
            
            # Refresh sessions list
            self.refresh_sessions_list()
            
            QMessageBox.information(self, "Success", "TaskWeaver initialized successfully!")
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to initialize TaskWeaver: {str(e)}")
    
    def refresh_sessions_list(self):
        """Refresh the list of available sessions"""
        if not self.taskweaver_app:
            return
        
        self.sessions_list.clear()
        self.sessions = self.taskweaver_app.list_sessions()
        
        for session_id, session in self.sessions.items():
            item = QListWidgetItem(session.metadata.name or session_id)
            item.setData(Qt.UserRole, session_id)
            self.sessions_list.addItem(item)
    
    def create_new_session(self):
        """Create a new session"""
        if not self.taskweaver_app:
            QMessageBox.warning(self, "Warning", "Please initialize TaskWeaver first.")
            return
        
        session_name = f"Session {self.sessions_list.count() + 1}"
        session = self.taskweaver_app.create_session(session_name=session_name)
        
        item = QListWidgetItem(session.metadata.name or session.session_id)
        item.setData(Qt.UserRole, session.session_id)
        self.sessions_list.addItem(item)
        
        # Select the new session
        self.sessions_list.setCurrentItem(item)
        self.select_session(item)
    
    def select_session(self, item):
        """Select a session from the list"""
        session_id = item.data(Qt.UserRole)
        self.current_session = self.taskweaver_app.get_session(session_id)
        
        # Clear chat history and plan view
        self.chat_history.clear()
        self.plan_view.clear()
        
        # Display session history if available
        if hasattr(self.current_session, 'memory') and self.current_session.memory:
            conversation = self.current_session.memory.get_conversation()
            for round_item in conversation.rounds:
                for post in round_item.posts:
                    role = post.role
                    content = post.content
                    self.append_message(role, content)
        
        # Update plan view if available
        self.update_plan_view()
    
    def delete_session(self):
        """Delete the selected session"""
        if not self.current_session:
            QMessageBox.warning(self, "Warning", "Please select a session first.")
            return
        
        confirm = QMessageBox.question(
            self, 
            "Confirm Deletion", 
            f"Are you sure you want to delete session '{self.current_session.metadata.name}'?",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if confirm == QMessageBox.Yes:
            session_id = self.current_session.session_id
            self.taskweaver_app.delete_session(session_id)
            self.refresh_sessions_list()
            self.current_session = None
            self.chat_history.clear()
            self.plan_view.clear()
    
    def send_message(self):
        """Send a message to the current session"""
        if not self.current_session:
            QMessageBox.warning(self, "Warning", "Please select a session first.")
            return
        
        message = self.chat_input.text().strip()
        if not message:
            return
        
        # Append user message to chat history
        self.append_message("user", message)
        self.chat_input.clear()
        
        # Create worker thread to handle chat
        self.chat_worker = ChatWorker(self.current_session, message)
        self.chat_worker.response_received.connect(self.handle_response)
        self.chat_worker.error_occurred.connect(self.handle_error)
        self.chat_worker.start()
    
    def handle_response(self, response):
        """Handle the response from the chat worker"""
        self.append_message("assistant", response)
        self.update_plan_view()
    
    def handle_error(self, error_message):
        """Handle errors from the chat worker"""
        QMessageBox.critical(self, "Error", f"An error occurred: {error_message}")
    
    def append_message(self, role, content):
        """Append a message to the chat history"""
        cursor = self.chat_history.textCursor()
        cursor.movePosition(QTextCursor.End)
        
        # Format based on role
        if role.lower() == "user":
            cursor.insertHtml(f"<p><b>User:</b> {content}</p>")
        else:
            cursor.insertHtml(f"<p><b>TaskWeaver:</b> {content}</p>")
        
        # Scroll to bottom
        cursor.movePosition(QTextCursor.End)
        self.chat_history.setTextCursor(cursor)
    
    def update_plan_view(self):
        """Update the plan view with the current session's plan"""
        if not self.current_session:
            return
        
        # This is a simplified implementation
        # In a real implementation, you would extract the plan from the session's memory
        # For now, we'll just display a placeholder
        
        try:
            # Try to extract plan from memory
            if hasattr(self.current_session, 'memory') and self.current_session.memory:
                conversation = self.current_session.memory.get_conversation()
                
                # Look for plan information in the conversation
                plan_text = "# Current Plan\n\n"
                has_plan = False
                
                for round_item in conversation.rounds:
                    for post in round_item.posts:
                        if post.role.lower() == "assistant" and "plan" in post.content.lower():
                            # Extract plan-like content
                            lines = post.content.split("\n")
                            for line in lines:
                                if any(keyword in line.lower() for keyword in ["step", "task", "plan", "phase"]):
                                    plan_text += f"- {line.strip()}\n"
                                    has_plan = True
                
                if not has_plan:
                    plan_text += "No detailed plan has been created yet."
                
                self.plan_view.setText(plan_text)
            else:
                self.plan_view.setText("No plan information available.")
        except Exception as e:
            self.plan_view.setText(f"Error retrieving plan: {str(e)}")


def main():
    app = QApplication(sys.argv)
    gui = TaskWeaverGUI()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()

