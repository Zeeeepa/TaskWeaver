#!/usr/bin/env python3
"""
Enhanced TaskWeaver UI class with Codegen integration for deployment tasks
"""

import os
import json
import logging
from typing import Dict, List, Optional, Any, Union, Tuple

from injector import inject

from standalone_taskweaver.app.app import TaskWeaverApp
from standalone_taskweaver.config.config_mgt import AppConfigSource
from standalone_taskweaver.logging import TelemetryLogger
from standalone_taskweaver.codegen_agent.integration import CodegenIntegration
from standalone_taskweaver.codegen_agent.bidirectional_context import BidirectionalContext
from standalone_taskweaver.codegen_agent.advanced_api import CodegenAdvancedAPI
from standalone_taskweaver.codegen_agent.planner_integration import CodegenPlannerIntegration
from standalone_taskweaver.codegen_agent.weaver_integration import WeaverCodegenIntegration

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("taskweaver-ui-enhanced")

class TaskWeaverUIEnhanced:
    """
    Enhanced TaskWeaver UI class with Codegen integration for deployment tasks
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
        
        # Initialize components
        self.codegen_integration = CodegenIntegration(app, config, logger)
        self.context_manager = BidirectionalContext(app, config, logger, None)
        self.advanced_api = None
        self.planner_integration = None
        self.weaver_integration = None
        
        # Initialize context manager
        self.context_manager.initialize()
        
    def initialize_integration(self, 
                              github_token: str,
                              codegen_token: str,
                              ngrok_token: str,
                              codegen_org_id: str) -> bool:
        """
        Initialize Codegen integration with API credentials
        
        Args:
            github_token: GitHub API token
            codegen_token: Codegen API token
            ngrok_token: ngrok API token
            codegen_org_id: Codegen organization ID
            
        Returns:
            bool: True if initialization was successful, False otherwise
        """
        try:
            # Initialize Codegen integration
            success = self.codegen_integration.initialize(
                github_token=github_token,
                codegen_token=codegen_token,
                ngrok_token=ngrok_token,
                codegen_org_id=codegen_org_id
            )
            
            if success:
                # Initialize advanced API
                self.advanced_api = CodegenAdvancedAPI(
                    self.app,
                    self.config,
                    self.logger,
                    self.codegen_integration,
                    self.context_manager
                )
                
                # Initialize planner integration
                self.planner_integration = CodegenPlannerIntegration(
                    self.app,
                    self.config,
                    self.logger,
                    self.codegen_integration
                )
                
                # Initialize weaver integration
                self.weaver_integration = WeaverCodegenIntegration(
                    self.app,
                    self.config,
                    self.logger,
                    self.codegen_integration
                )
            
            return success
        except Exception as e:
            self.logger.error(f"Error initializing Codegen integration: {str(e)}")
            return False
    
    def is_deployment_task(self, task_description: str) -> bool:
        """
        Determine if a task is deployment-related
        
        Args:
            task_description: Task description
            
        Returns:
            bool: True if the task is deployment-related, False otherwise
        """
        if not self.weaver_integration:
            return False
        
        return self.weaver_integration.is_deployment_task(task_description)
    
    def create_deployment_task(self, task_description: str, context: Dict[str, Any] = None) -> str:
        """
        Create a deployment task
        
        Args:
            task_description: Task description
            context: Optional context for the task
            
        Returns:
            str: Task ID
        """
        if not self.weaver_integration:
            raise ValueError("Weaver integration not initialized")
        
        return self.weaver_integration.create_deployment_task(task_description, context)
    
    def delegate_deployment_task(self, task_id: str) -> bool:
        """
        Delegate a deployment task to Codegen
        
        Args:
            task_id: Task ID
            
        Returns:
            bool: True if the task was delegated successfully, False otherwise
        """
        if not self.weaver_integration:
            raise ValueError("Weaver integration not initialized")
        
        return self.weaver_integration.delegate_to_codegen(task_id)
    
    def get_deployment_task_status(self, task_id: str) -> Dict[str, Any]:
        """
        Get the status of a deployment task
        
        Args:
            task_id: Task ID
            
        Returns:
            Dict[str, Any]: Task status
        """
        if not self.weaver_integration:
            raise ValueError("Weaver integration not initialized")
        
        return self.weaver_integration.get_deployment_task_status(task_id)
    
    def get_deployment_task_results(self, task_id: str) -> Dict[str, Any]:
        """
        Get the results of a deployment task
        
        Args:
            task_id: Task ID
            
        Returns:
            Dict[str, Any]: Task results
        """
        if not self.weaver_integration:
            raise ValueError("Weaver integration not initialized")
        
        return self.weaver_integration.get_deployment_task_results(task_id)
    
    def generate_deployment_report(self, task_id: str) -> Dict[str, Any]:
        """
        Generate a report for a deployment task
        
        Args:
            task_id: Task ID
            
        Returns:
            Dict[str, Any]: Deployment report
        """
        if not self.weaver_integration:
            raise ValueError("Weaver integration not initialized")
        
        return self.weaver_integration.generate_deployment_report(task_id)
    
    def add_deployment_to_memory(self, task_id: str, planner_id: str) -> bool:
        """
        Add deployment task results to TaskWeaver's memory
        
        Args:
            task_id: Task ID
            planner_id: Planner ID
            
        Returns:
            bool: True if the results were added successfully, False otherwise
        """
        if not self.weaver_integration:
            raise ValueError("Weaver integration not initialized")
        
        planner = self.app.get_planner(planner_id)
        
        if not planner:
            raise ValueError(f"Planner {planner_id} not found")
        
        return self.weaver_integration.add_to_memory(task_id, planner)
    
    def cancel_deployment_task(self, task_id: str) -> bool:
        """
        Cancel a deployment task
        
        Args:
            task_id: Task ID
            
        Returns:
            bool: True if the task was cancelled successfully, False otherwise
        """
        if not self.weaver_integration:
            raise ValueError("Weaver integration not initialized")
        
        return self.weaver_integration.cancel_deployment_task(task_id)
    
    def list_deployment_tasks(self) -> List[Dict[str, Any]]:
        """
        List all deployment tasks
        
        Returns:
            List[Dict[str, Any]]: List of deployment tasks
        """
        if not self.weaver_integration:
            raise ValueError("Weaver integration not initialized")
        
        return self.weaver_integration.list_deployment_tasks()
    
    def get_integration_status(self) -> Dict[str, bool]:
        """
        Get the status of all integrations
        
        Returns:
            Dict[str, bool]: Status of all integrations
        """
        return {
            "codegen_integration": self.codegen_integration.is_initialized,
            "context_manager": self.context_manager is not None,
            "advanced_api": self.advanced_api is not None,
            "planner_integration": self.planner_integration is not None,
            "weaver_integration": self.weaver_integration is not None
        }
    
    # Include other methods from the original TaskWeaverUI class
    def get_github_repos(self) -> List[Dict[str, Any]]:
        """
        Get a list of GitHub repositories
        
        Returns:
            List[Dict[str, Any]]: List of GitHub repositories
        """
        if not self.codegen_integration.is_initialized:
            return []
        
        return self.codegen_integration.github_manager.get_repos()
    
    def get_github_repo(self, repo_name: str) -> Dict[str, Any]:
        """
        Get details of a GitHub repository
        
        Args:
            repo_name: Repository name
            
        Returns:
            Dict[str, Any]: Repository details
        """
        if not self.codegen_integration.is_initialized:
            return {}
        
        return self.codegen_integration.github_manager.get_repo(repo_name)
    
    def get_github_repo_files(self, repo_name: str, path: str = "") -> List[Dict[str, Any]]:
        """
        Get files in a GitHub repository
        
        Args:
            repo_name: Repository name
            path: Path in the repository
            
        Returns:
            List[Dict[str, Any]]: List of files
        """
        if not self.codegen_integration.is_initialized:
            return []
        
        return self.codegen_integration.github_manager.get_repo_files(repo_name, path)
    
    def get_github_file_content(self, repo_name: str, path: str) -> str:
        """
        Get the content of a file in a GitHub repository
        
        Args:
            repo_name: Repository name
            path: Path to the file
            
        Returns:
            str: File content
        """
        if not self.codegen_integration.is_initialized:
            return ""
        
        return self.codegen_integration.github_manager.get_file_content(repo_name, path)
    
    def search_github_code(self, query: str) -> List[Dict[str, Any]]:
        """
        Search for code in GitHub repositories
        
        Args:
            query: Search query
            
        Returns:
            List[Dict[str, Any]]: Search results
        """
        if not self.codegen_integration.is_initialized:
            return []
        
        return self.codegen_integration.github_manager.search_code(query)
    
    def is_code_related_task(self, task_description: str) -> bool:
        """
        Determine if a task is code-related
        
        Args:
            task_description: Task description
            
        Returns:
            bool: True if the task is code-related, False otherwise
        """
        if not self.planner_integration:
            return False
        
        return self.planner_integration.is_code_related_task(task_description)
    
    def delegate_to_codegen(self, task_description: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Delegate a task to Codegen
        
        Args:
            task_description: Task description
            context: Optional context for the task
            
        Returns:
            Dict[str, Any]: Result of the task
        """
        if not self.planner_integration:
            raise ValueError("Planner integration not initialized")
        
        return self.planner_integration.delegate_to_codegen(task_description, context)

