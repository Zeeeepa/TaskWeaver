#!/usr/bin/env python3
"""
Integration module for Codegen and TaskWeaver
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
        self.is_initialized = False
        
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
            
    def get_repositories(self) -> List[Dict[str, str]]:
        """
        Get list of GitHub repositories
        
        Returns:
            List[Dict[str, str]]: List of repository information with name and description
        """
        if not self.github_manager:
            self.logger.error("GitHub manager not initialized")
            return []
            
        try:
            repos = []
            user = self.github_manager.github_client.get_user()
            for repo in user.get_repos():
                repos.append({
                    "name": repo.full_name,
                    "description": repo.description or "",
                    "url": repo.html_url,
                    "stars": repo.stargazers_count,
                    "forks": repo.forks_count,
                    "language": repo.language or "Unknown"
                })
            return repos
        except Exception as e:
            self.logger.error(f"Error getting GitHub repositories: {str(e)}")
            return []
            
    def create_codegen_task(self, prompt: str, repo_name: Optional[str] = None) -> Optional[str]:
        """
        Create a Codegen task
        
        Args:
            prompt: Task prompt
            repo_name: Optional repository name to use for this task
            
        Returns:
            Optional[str]: Task ID if successful, None otherwise
        """
        if not self.codegen_manager:
            self.logger.error("Codegen manager not initialized")
            return None
            
        try:
            # Set repository if provided
            if repo_name and self.codegen_config.repo_name != repo_name:
                self.set_repository(repo_name)
                
            # Create a Codegen task
            task = self.codegen_manager.agent.run(prompt=prompt)
            
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
            Optional[Dict[str, Any]]: Task status information if successful, None otherwise
        """
        if not self.codegen_manager:
            self.logger.error("Codegen manager not initialized")
            return None
            
        try:
            # Get task status
            task = self.codegen_manager.agent.get_task(task_id)
            
            if not task:
                self.logger.error(f"Task with ID {task_id} not found")
                return None
                
            return {
                "id": task.id,
                "status": task.status,
                "created_at": task.created_at,
                "updated_at": task.updated_at,
                "completed": task.completed,
                "result": task.result if hasattr(task, "result") else None
            }
        except Exception as e:
            self.logger.error(f"Error getting task status: {str(e)}")
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
            
    def get_status(self) -> Dict[str, Any]:
        """
        Get the status of the Codegen integration
        
        Returns:
            Dict[str, Any]: Status information
        """
        status = {
            "initialized": self.is_initialized,
            "github_connected": self.github_manager is not None,
            "codegen_connected": self.codegen_manager is not None,
            "ngrok_connected": self.ngrok_manager is not None,
            "workflow_manager": self.workflow_manager is not None,
            "repository": self.codegen_config.repo_name if self.codegen_config else None
        }
        
        return status
            
    def create_requirements_document(self, requirements: str) -> Tuple[bool, Optional[str]]:
        """
        Create or update a REQUIREMENTS.md file in the repository
        
        Args:
            requirements: Requirements content
            
        Returns:
            Tuple[bool, Optional[str]]: (Success status, Error message if any)
        """
        if not self.github_manager or not self.codegen_config.repo_name:
            return False, "GitHub manager not initialized or repository not set"
            
        try:
            repo = self.github_manager.github_client.get_repo(self.codegen_config.repo_name)
            
            # Check if file exists
            try:
                contents = repo.get_contents("REQUIREMENTS.md")
                # Update file
                repo.update_file(
                    path="REQUIREMENTS.md",
                    message="Update requirements document",
                    content=requirements,
                    sha=contents.sha
                )
            except Exception:
                # Create file
                repo.create_file(
                    path="REQUIREMENTS.md",
                    message="Create requirements document",
                    content=requirements
                )
                
            return True, None
        except Exception as e:
            error_msg = f"Error creating requirements document: {str(e)}"
            self.logger.error(error_msg)
            return False, error_msg
            
    def parse_requirements_document(self) -> Optional[Dict[str, Any]]:
        """
        Parse the REQUIREMENTS.md file from the repository
        
        Returns:
            Optional[Dict[str, Any]]: Parsed requirements if successful, None otherwise
        """
        if not self.github_manager or not self.codegen_config.repo_name:
            self.logger.error("GitHub manager not initialized or repository not set")
            return None
            
        try:
            repo = self.github_manager.github_client.get_repo(self.codegen_config.repo_name)
            
            # Get the file content
            try:
                contents = repo.get_contents("REQUIREMENTS.md")
                content = contents.decoded_content.decode("utf-8")
                
                # Parse the content
                from standalone_taskweaver.codegen_agent.requirements_manager import RequirementsManager
                requirements_manager = RequirementsManager(self.app, self.config, self.logger, self)
                parsed_requirements = requirements_manager.parse_requirements_document(content)
                
                return parsed_requirements
            except Exception as e:
                self.logger.error(f"Error getting requirements document: {str(e)}")
                return None
        except Exception as e:
            self.logger.error(f"Error parsing requirements document: {str(e)}")
            return None
            
    def generate_concurrent_queries(self, phase: int = 1) -> List[str]:
        """
        Generate concurrent queries for a specific phase
        
        Args:
            phase: Phase number (1-based)
            
        Returns:
            List[str]: List of queries
        """
        try:
            # Parse the requirements document
            parsed_requirements = self.parse_requirements_document()
            
            if not parsed_requirements:
                self.logger.error("Failed to parse requirements document")
                return []
                
            # Generate queries
            from standalone_taskweaver.codegen_agent.requirements_manager import RequirementsManager
            requirements_manager = RequirementsManager(self.app, self.config, self.logger, self)
            queries = requirements_manager.generate_concurrent_queries(parsed_requirements, phase)
            
            return queries
        except Exception as e:
            self.logger.error(f"Error generating concurrent queries: {str(e)}")
            return []
