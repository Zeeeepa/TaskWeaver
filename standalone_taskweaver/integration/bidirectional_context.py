#!/usr/bin/env python3
"""
Bidirectional Context Manager

This module provides a bidirectional context manager for sharing context between TaskWeaver and Codegen.
"""

import os
import sys
import json
import logging
from typing import Dict, List, Optional, Any, Union, Tuple

from injector import inject

from standalone_taskweaver.app.app import TaskWeaverApp
from standalone_taskweaver.config.config_mgt import AppConfigSource
from standalone_taskweaver.logging import TelemetryLogger
from standalone_taskweaver.integration.codegen_integration import CodegenIntegration

class BidirectionalContext:
    """
    Bidirectional context manager for sharing context between TaskWeaver and Codegen
    """
    
    @inject
    def __init__(
        self,
        app: TaskWeaverApp,
        config: AppConfigSource,
        logger: TelemetryLogger,
        codegen_integration: Optional[CodegenIntegration] = None,
    ) -> None:
        self.app = app
        self.config = config
        self.logger = logger
        self.codegen_integration = codegen_integration
        self.taskweaver_context = {}
        self.codegen_context = {}
        self.shared_context = {}
        
    def initialize(self) -> bool:
        """
        Initialize the context manager
        
        Returns:
            bool: True if initialization was successful, False otherwise
        """
        try:
            # Initialize context dictionaries
            self.taskweaver_context = {
                "variables": {},
                "memory": {},
                "history": []
            }
            
            self.codegen_context = {
                "variables": {},
                "memory": {},
                "history": []
            }
            
            self.shared_context = {
                "variables": {},
                "memory": {},
                "history": [],
                "files": {},
                "issues": {},
                "prs": {}
            }
            
            self.logger.info("Bidirectional context manager initialized")
            return True
        except Exception as e:
            self.logger.error(f"Error initializing bidirectional context manager: {str(e)}")
            return False
            
    def update_taskweaver_context(self, context_update: Dict[str, Any]) -> bool:
        """
        Update TaskWeaver context
        
        Args:
            context_update: Context update from TaskWeaver
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            # Update TaskWeaver context
            for key, value in context_update.items():
                if key in self.taskweaver_context:
                    if isinstance(self.taskweaver_context[key], dict) and isinstance(value, dict):
                        self.taskweaver_context[key].update(value)
                    else:
                        self.taskweaver_context[key] = value
                else:
                    self.taskweaver_context[key] = value
                    
            # Update shared context
            self._update_shared_context()
            
            self.logger.info("TaskWeaver context updated")
            return True
        except Exception as e:
            self.logger.error(f"Error updating TaskWeaver context: {str(e)}")
            return False
            
    def update_codegen_context(self, context_update: Dict[str, Any]) -> bool:
        """
        Update Codegen context
        
        Args:
            context_update: Context update from Codegen
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            # Update Codegen context
            for key, value in context_update.items():
                if key in self.codegen_context:
                    if isinstance(self.codegen_context[key], dict) and isinstance(value, dict):
                        self.codegen_context[key].update(value)
                    else:
                        self.codegen_context[key] = value
                else:
                    self.codegen_context[key] = value
                    
            # Update shared context
            self._update_shared_context()
            
            self.logger.info("Codegen context updated")
            return True
        except Exception as e:
            self.logger.error(f"Error updating Codegen context: {str(e)}")
            return False
            
    def _update_shared_context(self) -> None:
        """
        Update shared context based on TaskWeaver and Codegen contexts
        """
        # Update variables
        for key, value in self.taskweaver_context.get("variables", {}).items():
            self.shared_context["variables"][key] = value
            
        for key, value in self.codegen_context.get("variables", {}).items():
            self.shared_context["variables"][key] = value
            
        # Update memory
        for key, value in self.taskweaver_context.get("memory", {}).items():
            self.shared_context["memory"][key] = value
            
        for key, value in self.codegen_context.get("memory", {}).items():
            self.shared_context["memory"][key] = value
            
        # Update history
        taskweaver_history = self.taskweaver_context.get("history", [])
        codegen_history = self.codegen_context.get("history", [])
        
        # Merge and sort history by timestamp
        merged_history = taskweaver_history + codegen_history
        merged_history.sort(key=lambda x: x.get("timestamp", 0))
        
        self.shared_context["history"] = merged_history
        
    def get_shared_context(self) -> Dict[str, Any]:
        """
        Get shared context
        
        Returns:
            Dict[str, Any]: Shared context
        """
        return self.shared_context
        
    def add_issue_to_context(self, issue_number: int) -> bool:
        """
        Add a GitHub issue to the context
        
        Args:
            issue_number: GitHub issue number
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            # This is a placeholder since we don't have direct access to GitHub API
            # In a real implementation, you would use PyGithub to get the issue
            
            # Add issue to shared context
            self.shared_context["issues"][str(issue_number)] = {
                "number": issue_number,
                "title": f"Issue #{issue_number}",
                "body": f"This is a placeholder for issue #{issue_number}",
                "state": "open",
                "created_at": "2023-01-01T00:00:00Z",
                "updated_at": "2023-01-01T00:00:00Z"
            }
            
            self.logger.info(f"Added issue #{issue_number} to context")
            return True
        except Exception as e:
            self.logger.error(f"Error adding issue to context: {str(e)}")
            return False
            
    def add_pr_to_context(self, pr_number: int) -> bool:
        """
        Add a GitHub pull request to the context
        
        Args:
            pr_number: GitHub pull request number
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            # This is a placeholder since we don't have direct access to GitHub API
            # In a real implementation, you would use PyGithub to get the PR
            
            # Add PR to shared context
            self.shared_context["prs"][str(pr_number)] = {
                "number": pr_number,
                "title": f"PR #{pr_number}",
                "body": f"This is a placeholder for PR #{pr_number}",
                "state": "open",
                "created_at": "2023-01-01T00:00:00Z",
                "updated_at": "2023-01-01T00:00:00Z"
            }
            
            self.logger.info(f"Added PR #{pr_number} to context")
            return True
        except Exception as e:
            self.logger.error(f"Error adding PR to context: {str(e)}")
            return False
            
    def add_file_to_context(self, file_path: str) -> bool:
        """
        Add a file to the context
        
        Args:
            file_path: Path to the file
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            # This is a placeholder since we don't have direct access to the file system
            # In a real implementation, you would read the file and add it to the context
            
            # Add file to shared context
            self.shared_context["files"][file_path] = {
                "path": file_path,
                "content": f"This is a placeholder for file {file_path}",
                "language": "python" if file_path.endswith(".py") else "text",
                "last_modified": "2023-01-01T00:00:00Z"
            }
            
            self.logger.info(f"Added file {file_path} to context")
            return True
        except Exception as e:
            self.logger.error(f"Error adding file to context: {str(e)}")
            return False

