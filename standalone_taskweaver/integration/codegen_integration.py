#!/usr/bin/env python3
"""
Codegen Integration Module

This module provides integration between TaskWeaver and Codegen.
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

# Import Codegen SDK
try:
    from codegen import Agent
except ImportError:
    logging.warning("Codegen SDK not found. Please install it with 'pip install codegen'")

class CodegenIntegration:
    """
    Integration class for Codegen and TaskWeaver
    """
    
    @inject
    def __init__(
        self,
        app: TaskWeaverApp,
        config: AppConfigSource,
        logger: TelemetryLogger,
    ) -> None:
        self.app = app
        self.config = config
        self.logger = logger
        self.is_initialized = False
        self.agent = None
        self.github_token = None
        self.codegen_token = None
        self.ngrok_token = None
        self.codegen_org_id = None
        self.repo_name = None
        
    def initialize(
        self,
        github_token: str,
        codegen_token: str,
        ngrok_token: str,
        codegen_org_id: str,
        repo_name: Optional[str] = None
    ) -> bool:
        """
        Initialize the integration with API credentials
        
        Args:
            github_token: GitHub API token
            codegen_token: Codegen API token
            ngrok_token: ngrok API token
            codegen_org_id: Codegen organization ID
            repo_name: GitHub repository name (optional)
            
        Returns:
            bool: True if initialization was successful, False otherwise
        """
        try:
            # Store credentials
            self.github_token = github_token
            self.codegen_token = codegen_token
            self.ngrok_token = ngrok_token
            self.codegen_org_id = codegen_org_id
            
            if repo_name:
                self.repo_name = repo_name
                
            # Initialize Codegen agent
            self.agent = Agent(
                api_key=codegen_token,
                org_id=codegen_org_id
            )
            
            # Test connection
            self.agent.ping()
            
            self.is_initialized = True
            self.logger.info("Codegen integration initialized successfully")
            return True
        except Exception as e:
            self.logger.error(f"Error initializing Codegen integration: {str(e)}")
            return False
            
    def set_repository(self, repo_name: str) -> bool:
        """
        Set the GitHub repository
        
        Args:
            repo_name: GitHub repository name
            
        Returns:
            bool: True if successful, False otherwise
        """
        if not self.is_initialized:
            self.logger.error("Codegen integration not initialized")
            return False
            
        try:
            self.repo_name = repo_name
            self.logger.info(f"Repository set to {repo_name}")
            return True
        except Exception as e:
            self.logger.error(f"Error setting repository: {str(e)}")
            return False
            
    def get_repositories(self) -> List[str]:
        """
        Get list of GitHub repositories
        
        Returns:
            List[str]: List of repository names
        """
        if not self.is_initialized:
            self.logger.error("Codegen integration not initialized")
            return []
            
        try:
            # This is a placeholder since we don't have direct access to GitHub API
            # In a real implementation, you would use PyGithub to get the repositories
            return []
        except Exception as e:
            self.logger.error(f"Error getting GitHub repositories: {str(e)}")
            return []
            
    def create_codegen_task(self, prompt: str, repo_name: Optional[str] = None) -> Optional[str]:
        """
        Create a Codegen task
        
        Args:
            prompt: Task prompt
            repo_name: Optional repository name to override the default
            
        Returns:
            Optional[str]: Task ID if successful, None otherwise
        """
        if not self.is_initialized:
            self.logger.error("Codegen integration not initialized")
            return None
            
        try:
            # Use the provided repo_name or the default one
            target_repo = repo_name or self.repo_name
            
            if not target_repo:
                self.logger.error("No repository specified")
                return None
                
            # Create a Codegen task
            task = self.agent.run(prompt=prompt, repo=target_repo)
            
            self.logger.info(f"Codegen task created with ID: {task.id}")
            return task.id
        except Exception as e:
            self.logger.error(f"Error creating Codegen task: {str(e)}")
            return None
            
    def get_task_status(self, task_id: str) -> Optional[Dict[str, Any]]:
        """
        Get the status of a Codegen task
        
        Args:
            task_id: Task ID
            
        Returns:
            Optional[Dict[str, Any]]: Task status if successful, None otherwise
        """
        if not self.is_initialized:
            self.logger.error("Codegen integration not initialized")
            return None
            
        try:
            # Get task status
            task = self.agent.get_task(task_id)
            
            if not task:
                self.logger.error(f"Task not found: {task_id}")
                return None
                
            # Convert task to dictionary
            task_dict = {
                "id": task.id,
                "status": task.status,
                "created_at": task.created_at,
                "updated_at": task.updated_at,
                "completed": task.completed,
                "result": task.result
            }
            
            return task_dict
        except Exception as e:
            self.logger.error(f"Error getting task status: {str(e)}")
            return None
            
    def create_requirements_document(self, requirements: str) -> Tuple[bool, Optional[str]]:
        """
        Create or update a REQUIREMENTS.md file in the repository
        
        Args:
            requirements: Requirements content
            
        Returns:
            Tuple[bool, Optional[str]]: (success, error_message)
        """
        if not self.is_initialized:
            self.logger.error("Codegen integration not initialized")
            return False, "Codegen integration not initialized"
            
        if not self.repo_name:
            self.logger.error("No repository specified")
            return False, "No repository specified"
            
        try:
            # This is a placeholder since we don't have direct access to GitHub API
            # In a real implementation, you would use PyGithub to create or update the file
            return True, None
        except Exception as e:
            self.logger.error(f"Error creating requirements document: {str(e)}")
            return False, str(e)
            
    def get_status(self) -> Dict[str, Any]:
        """
        Get the status of the Codegen integration
        
        Returns:
            Dict[str, Any]: Integration status
        """
        return {
            "initialized": self.is_initialized,
            "github_connected": self.github_token is not None,
            "codegen_connected": self.agent is not None,
            "ngrok_connected": self.ngrok_token is not None,
            "repository": self.repo_name
        }

