#!/usr/bin/env python3
"""
Integration module for Codegen and TaskWeaver
"""

import os
import sys
import json
import logging
from typing import Dict, List, Optional, Any, Union

from injector import inject

from standalone_taskweaver.app.app import TaskWeaverApp
from standalone_taskweaver.config.config_mgt import AppConfigSource
from standalone_taskweaver.logging import TelemetryLogger
from standalone_taskweaver.codegen_agent.codegen import Configuration, GitHubManager, NgrokManager, CodegenManager, WorkflowManager

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("codegen-integration")

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
        self.codegen_config = None
        self.github_manager = None
        self.codegen_manager = None
        self.ngrok_manager = None
        self.workflow_manager = None
        
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
            # Create configuration
            self.codegen_config = Configuration()
            self.codegen_config.github_token = github_token
            self.codegen_config.codegen_token = codegen_token
            self.codegen_config.ngrok_token = ngrok_token
            self.codegen_config.codegen_org_id = codegen_org_id
            
            if repo_name:
                self.codegen_config.repo_name = repo_name
                
            # Initialize managers
            self.github_manager = GitHubManager(self.codegen_config)
            self.codegen_manager = CodegenManager(self.codegen_config)
            self.ngrok_manager = NgrokManager(self.codegen_config)
            
            # Only initialize workflow manager if repo_name is provided
            if repo_name:
                self.workflow_manager = WorkflowManager(self.codegen_config)
                
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
        if not self.codegen_config:
            self.logger.error("Codegen integration not initialized")
            return False
            
        try:
            self.codegen_config.repo_name = repo_name
            
            # Initialize workflow manager if not already initialized
            if not self.workflow_manager:
                self.workflow_manager = WorkflowManager(self.codegen_config)
            else:
                # Update the repository name in the workflow manager
                self.workflow_manager.config.repo_name = repo_name
                
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
        if not self.github_manager:
            self.logger.error("GitHub manager not initialized")
            return []
            
        try:
            repos = []
            user = self.github_manager.github_client.get_user()
            for repo in user.get_repos():
                repos.append(repo.full_name)
            return repos
        except Exception as e:
            self.logger.error(f"Error getting GitHub repositories: {str(e)}")
            return []
            
    def create_codegen_task(self, prompt: str) -> Optional[str]:
        """
        Create a Codegen task
        
        Args:
            prompt: Task prompt
            
        Returns:
            Optional[str]: Task ID if successful, None otherwise
        """
        if not self.codegen_manager:
            self.logger.error("Codegen manager not initialized")
            return None
            
        try:
            # Create a Codegen task
            task = self.codegen_manager.agent.run(prompt=prompt)
            
            self.logger.info(f"Codegen task created with ID: {task.id}")
            return task.id
        except Exception as e:
            self.logger.error(f"Error creating Codegen task: {str(e)}")
            return None
            
    def start_workflow(self) -> bool:
        """
        Start the Codegen workflow
        
        Returns:
            bool: True if successful, False otherwise
        """
        if not self.workflow_manager:
            self.logger.error("Workflow manager not initialized")
            return False
            
        try:
            # Start the workflow
            success = self.workflow_manager.start()
            
            if success:
                self.logger.info("Workflow started successfully")
            else:
                self.logger.error("Failed to start workflow")
                
            return success
        except Exception as e:
            self.logger.error(f"Error starting workflow: {str(e)}")
            return False
            
    def stop_workflow(self) -> bool:
        """
        Stop the Codegen workflow
        
        Returns:
            bool: True if successful, False otherwise
        """
        if not self.workflow_manager:
            self.logger.error("Workflow manager not initialized")
            return False
            
        try:
            # Stop the workflow
            self.workflow_manager.stop()
            
            self.logger.info("Workflow stopped successfully")
            return True
        except Exception as e:
            self.logger.error(f"Error stopping workflow: {str(e)}")
            return False

