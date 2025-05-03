#!/usr/bin/env python3
"""
Bidirectional Context Manager for TaskWeaver and Codegen

This module provides a bidirectional context manager that maintains a shared
understanding between TaskWeaver and Codegen, allowing insights from either
system to inform the other.
"""

import os
import sys
import json
import logging
from typing import Dict, List, Optional, Any, Union, Tuple
from pathlib import Path

from injector import inject

from standalone_taskweaver.app.app import TaskWeaverApp
from standalone_taskweaver.config.config_mgt import AppConfigSource
from standalone_taskweaver.logging import TelemetryLogger
from standalone_taskweaver.memory import Memory
from standalone_taskweaver.codegen_agent.context_manager import CodegenContext

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("bidirectional-context")

class BidirectionalContext:
    """
    Bidirectional context manager for TaskWeaver and Codegen
    """
    
    @inject
    def __init__(
        self,
        app: TaskWeaverApp,
        config: AppConfigSource,
        logger: TelemetryLogger,
        memory: Memory,
    ) -> None:
        self.app = app
        self.config = config
        self.logger = logger
        self.memory = memory
        self.codegen_context = CodegenContext()
        
        # Create a directory for context storage
        self.context_dir = Path(self.config.app_base_path) / ".context"
        self.context_dir.mkdir(exist_ok=True)
        
        # Initialize context
        self.taskweaver_context: Dict[str, Any] = {}
        self.codegen_context_data: Dict[str, Any] = {}
        self.shared_context: Dict[str, Any] = {}
        
    def initialize(self) -> None:
        """
        Initialize the context manager
        """
        try:
            # Initialize TaskWeaver context
            self._initialize_taskweaver_context()
            
            # Initialize Codegen context
            self._initialize_codegen_context()
            
            # Create shared context
            self._create_shared_context()
            
            self.logger.info("Bidirectional context initialized successfully")
        except Exception as e:
            self.logger.error(f"Error initializing bidirectional context: {str(e)}")
    
    def _initialize_taskweaver_context(self) -> None:
        """
        Initialize TaskWeaver context
        """
        # Get session information
        sessions = self.app.list_sessions()
        
        # Extract relevant information from sessions
        session_data = {}
        for session_id, session in sessions.items():
            session_data[session_id] = {
                "id": session_id,
                "name": session.metadata.name,
                "created_at": session.metadata.created_at,
                "updated_at": session.metadata.updated_at,
                "variables": session.metadata.variables,
            }
        
        # Get memory information - create a dictionary representation of memory
        memory_data = {
            "rounds": [round.__dict__ for round in self.memory.get_rounds()],
            "shared_memory": {k.value: [entry.__dict__ for entry in v] 
                             for k, v in self.memory.shared_memory.items()}
        }
        
        # Create TaskWeaver context
        self.taskweaver_context = {
            "sessions": session_data,
            "memory": memory_data,
        }
    
    def _initialize_codegen_context(self) -> None:
        """
        Initialize Codegen context
        """
        # Collect repository metadata
        self.codegen_context.collect_repo_metadata()
        
        # Get Codegen context data
        self.codegen_context_data = self.codegen_context.context_data
    
    def _create_shared_context(self) -> None:
        """
        Create shared context between TaskWeaver and Codegen
        """
        # Merge TaskWeaver and Codegen contexts
        self.shared_context = {
            "taskweaver": self.taskweaver_context,
            "codegen": self.codegen_context_data,
            "shared": {
                "repository": self.codegen_context_data.get("repository", ""),
                "metadata": self.codegen_context_data.get("metadata", {}),
                "files": self.codegen_context_data.get("files", {}),
                "sessions": self.taskweaver_context.get("sessions", {}),
            }
        }
        
        # Save shared context to file
        self._save_shared_context()
    
    def _save_shared_context(self) -> None:
        """
        Save shared context to file
        """
        context_file = self.context_dir / "shared_context.json"
        with open(context_file, "w") as f:
            json.dump(self.shared_context, f, indent=2)
    
    def update_taskweaver_context(self, context_update: Dict[str, Any]) -> None:
        """
        Update TaskWeaver context
        
        Args:
            context_update: Context update from TaskWeaver
        """
        try:
            # Update TaskWeaver context
            self.taskweaver_context.update(context_update)
            
            # Update shared context
            self._update_shared_context()
            
            self.logger.info("TaskWeaver context updated successfully")
        except Exception as e:
            self.logger.error(f"Error updating TaskWeaver context: {str(e)}")
    
    def update_codegen_context(self, context_update: Dict[str, Any]) -> None:
        """
        Update Codegen context
        
        Args:
            context_update: Context update from Codegen
        """
        try:
            # Update Codegen context
            self.codegen_context_data.update(context_update)
            
            # Update shared context
            self._update_shared_context()
            
            self.logger.info("Codegen context updated successfully")
        except Exception as e:
            self.logger.error(f"Error updating Codegen context: {str(e)}")
    
    def _update_shared_context(self) -> None:
        """
        Update shared context
        """
        # Update shared context
        self.shared_context = {
            "taskweaver": self.taskweaver_context,
            "codegen": self.codegen_context_data,
            "shared": {
                "repository": self.codegen_context_data.get("repository", ""),
                "metadata": self.codegen_context_data.get("metadata", {}),
                "files": self.codegen_context_data.get("files", {}),
                "sessions": self.taskweaver_context.get("sessions", {}),
            }
        }
        
        # Save shared context to file
        self._save_shared_context()
    
    def get_shared_context(self) -> Dict[str, Any]:
        """
        Get shared context
        
        Returns:
            Dict[str, Any]: Shared context
        """
        return self.shared_context
    
    def get_taskweaver_context(self) -> Dict[str, Any]:
        """
        Get TaskWeaver context
        
        Returns:
            Dict[str, Any]: TaskWeaver context
        """
        return self.taskweaver_context
    
    def get_codegen_context(self) -> Dict[str, Any]:
        """
        Get Codegen context
        
        Returns:
            Dict[str, Any]: Codegen context
        """
        return self.codegen_context_data
    
    def add_issue_to_context(self, issue_number: int) -> None:
        """
        Add a GitHub issue to the context
        
        Args:
            issue_number: GitHub issue number
        """
        try:
            # Collect issue data
            self.codegen_context.collect_issue_data(issue_number)
            
            # Update shared context
            self._update_shared_context()
            
            self.logger.info(f"Issue #{issue_number} added to context successfully")
        except Exception as e:
            self.logger.error(f"Error adding issue to context: {str(e)}")
    
    def add_pr_to_context(self, pr_number: int) -> None:
        """
        Add a GitHub pull request to the context
        
        Args:
            pr_number: GitHub pull request number
        """
        try:
            # Collect PR data
            self.codegen_context.collect_pr_data(pr_number)
            
            # Update shared context
            self._update_shared_context()
            
            self.logger.info(f"PR #{pr_number} added to context successfully")
        except Exception as e:
            self.logger.error(f"Error adding PR to context: {str(e)}")
    
    def add_file_to_context(self, file_path: str) -> None:
        """
        Add a file to the context
        
        Args:
            file_path: Path to the file
        """
        try:
            # Read file content
            with open(file_path, "r") as f:
                content = f.read()
            
            # Add file to context
            self.codegen_context_data["files"][file_path] = {
                "path": file_path,
                "content": content,
                "size": len(content),
                "last_modified": os.path.getmtime(file_path),
            }
            
            # Update shared context
            self._update_shared_context()
            
            self.logger.info(f"File {file_path} added to context successfully")
        except Exception as e:
            self.logger.error(f"Error adding file to context: {str(e)}")
    
    def export_context_for_codegen(self) -> Dict[str, Any]:
        """
        Export context for Codegen
        
        Returns:
            Dict[str, Any]: Context for Codegen
        """
        # Create a context object for Codegen
        codegen_context = {
            "repository": self.shared_context["shared"]["repository"],
            "metadata": self.shared_context["shared"]["metadata"],
            "files": self.shared_context["shared"]["files"],
            "taskweaver_sessions": self.shared_context["shared"]["sessions"],
            "issues": self.codegen_context_data.get("issues", []),
            "pull_requests": self.codegen_context_data.get("pull_requests", []),
        }
        
        return codegen_context
    
    def export_context_for_taskweaver(self) -> Dict[str, Any]:
        """
        Export context for TaskWeaver
        
        Returns:
            Dict[str, Any]: Context for TaskWeaver
        """
        # Create a context object for TaskWeaver
        taskweaver_context = {
            "repository": self.shared_context["shared"]["repository"],
            "metadata": self.shared_context["shared"]["metadata"],
            "files": self.shared_context["shared"]["files"],
            "codegen_issues": self.codegen_context_data.get("issues", []),
            "codegen_pull_requests": self.codegen_context_data.get("pull_requests", []),
        }
        
        return taskweaver_context
