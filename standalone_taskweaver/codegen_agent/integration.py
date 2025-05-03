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
from codegen import Agent  # CodeGen SDK

from standalone_taskweaver.app.app import TaskWeaverApp
from standalone_taskweaver.config.config_mgt import AppConfigSource
from standalone_taskweaver.logging import TelemetryLogger
from standalone_taskweaver.memory import Memory
from standalone_taskweaver.codegen_agent.concurrent_execution import ConcurrentExecutionEngine, ErrorHandlingFramework
from standalone_taskweaver.codegen_agent.requirements_manager import AtomicTask, DependencyGraph, RequirementsManager
from standalone_taskweaver.codegen_agent.interface_generator import InterfaceGenerator
from standalone_taskweaver.codegen_agent.query_generation import QueryGenerationFramework
from standalone_taskweaver.codegen_agent.codegen import Configuration, GitHubManager, CodegenManager, NgrokManager, WorkflowManager

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
        
        # Initialize new components
        self.requirements_manager = RequirementsManager(app, config, logger)
        self.concurrent_execution_engine = ConcurrentExecutionEngine(app, config, logger)
        self.error_handling_framework = ErrorHandlingFramework(app, config, logger)
        self.interface_generator = InterfaceGenerator(app, config, logger)
        self.query_generation_framework = QueryGenerationFramework(app, config, logger)
        
        # Initialize Codegen agent
        self.codegen_agent = None
        
    def initialize(
        self,
        github_token: str,
        codegen_token: str,
        ngrok_token: str,
        codegen_org_id: str,
        repo_name: str = None,
    ) -> None:
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
            
            # Initialize Codegen agent
            self.codegen_agent = Agent(org_id=codegen_org_id, token=codegen_token)
            
            # Initialize new components with Codegen credentials
            self.concurrent_execution_engine.initialize(codegen_org_id, codegen_token)
            self.interface_generator.initialize(codegen_org_id, codegen_token)
            self.query_generation_framework.initialize(codegen_org_id, codegen_token)
            
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
        
    def create_requirements_file(self, content: str = None) -> None:
        """
        Create a REQUIREMENTS.md file with the given content or a template
        
        Args:
            content: Optional content for the file
        """
        self.requirements_manager.create_requirements_file(content)
        
    def create_structure_file(self, content: str = None) -> None:
        """
        Create a STRUCTURE.md file with the given content or a template
        
        Args:
            content: Optional content for the file
        """
        self.requirements_manager.create_structure_file(content)
        
    def parse_requirements(self) -> List[AtomicTask]:
        """
        Parse REQUIREMENTS.md into atomic tasks
        
        Returns:
            List of atomic tasks
        """
        return self.requirements_manager.parse_requirements()
        
    def parse_structure_file(self) -> Dict[str, Any]:
        """
        Parse STRUCTURE.md to extract requirements section
        
        Returns:
            Dictionary with parsed structure
        """
        return self.requirements_manager.parse_structure_file()
        
    def identify_dependencies(self, tasks: List[AtomicTask]) -> DependencyGraph:
        """
        Identify dependencies between tasks and create a dependency graph
        
        Args:
            tasks: List of atomic tasks
            
        Returns:
            Dependency graph
        """
        return self.requirements_manager.identify_dependencies(tasks)
        
    def prioritize_tasks(self, dependency_graph: DependencyGraph) -> List[List[AtomicTask]]:
        """
        Group tasks into phases based on dependencies, maximizing concurrency
        
        Args:
            dependency_graph: Dependency graph
            
        Returns:
            List of phases, each containing a list of tasks
        """
        return self.requirements_manager.prioritize_tasks(dependency_graph)
        
    async def execute_tasks(self, tasks: List[AtomicTask]) -> List[Any]:
        """
        Execute multiple tasks concurrently and return results
        
        Args:
            tasks: List of atomic tasks
            
        Returns:
            List of task results
        """
        return await self.concurrent_execution_engine.execute_tasks(tasks)
        
    async def monitor_progress(self, task_ids: List[str]) -> Dict[str, Any]:
        """
        Monitor progress of multiple concurrent tasks
        
        Args:
            task_ids: List of task IDs
            
        Returns:
            Dictionary mapping task IDs to statuses
        """
        return await self.concurrent_execution_engine.monitor_progress(task_ids)
        
    def generate_interface(self, component_spec: Dict[str, Any]) -> str:
        """
        Generate interface definition for a component
        
        Args:
            component_spec: Component specification
            
        Returns:
            Interface definition
        """
        return self.interface_generator.generate_interface(component_spec)
        
    def create_mock_implementation(self, interface: str) -> str:
        """
        Create mock implementation for an interface
        
        Args:
            interface: Interface definition
            
        Returns:
            Mock implementation
        """
        return self.interface_generator.create_mock_implementation(interface)
        
    def generate_queries(self, requirements: List[str], phase: int = 1) -> List[str]:
        """
        Generate optimized queries for a specific phase
        
        Args:
            requirements: List of requirements
            phase: Phase number (default: 1)
            
        Returns:
            List of queries
        """
        return self.query_generation_framework.generate_queries(requirements, phase)
        
    def generate_queries_from_tasks(self, tasks: List[AtomicTask], phase: int = 1) -> List[str]:
        """
        Generate optimized queries from atomic tasks for a specific phase
        
        Args:
            tasks: List of atomic tasks
            phase: Phase number (default: 1)
            
        Returns:
            List of queries
        """
        return self.query_generation_framework.generate_queries_from_tasks(tasks, phase)
        
    def optimize_for_concurrency(self, queries: List[str]) -> List[str]:
        """
        Optimize queries for maximum concurrency
        
        Args:
            queries: List of queries
            
        Returns:
            Optimized list of queries
        """
        return self.query_generation_framework.optimize_for_concurrency(queries)
        
    def execute_query(self, query: str) -> str:
        """
        Execute a query using the Codegen API
        
        Args:
            query: Query string
            
        Returns:
            Result string
        """
        return self.query_generation_framework.execute_query(query)
        
    def execute_queries(self, queries: List[str]) -> List[str]:
        """
        Execute multiple queries using the Codegen API
        
        Args:
            queries: List of query strings
            
        Returns:
            List of result strings
        """
        return self.query_generation_framework.execute_queries(queries)
        
    def execute_queries_concurrently(self, queries: List[str]) -> List[str]:
        """
        Execute multiple queries concurrently using the Codegen API
        
        Args:
            queries: List of query strings
            
        Returns:
            List of result strings
        """
        return self.query_generation_framework.execute_queries_concurrently(queries)
        
    def handle_error(self, task: AtomicTask, error: Exception) -> Any:
        """
        Handle errors with appropriate fallback strategies
        
        Args:
            task: Atomic task
            error: Exception
            
        Returns:
            Task result
        """
        return self.error_handling_framework.handle_error(task, error)
        
    def retry_with_backoff(self, task: AtomicTask, max_retries: int = 3) -> Any:
        """
        Retry failed tasks with exponential backoff
        
        Args:
            task: Atomic task
            max_retries: Maximum number of retries
            
        Returns:
            Task result
        """
        return self.error_handling_framework.retry_with_backoff(task, max_retries)
        
    def run_codegen_task(self, prompt: str) -> Any:
        """
        Run a task using the Codegen API
        
        Args:
            prompt: Prompt string
            
        Returns:
            Task result
        """
        if not self.codegen_agent:
            raise ValueError("Codegen agent not initialized. Call initialize() first.")
            
        # Execute the task using the Codegen SDK
        task = self.codegen_agent.run(prompt=prompt)
        
        # Return the task object
        return task
        
    def get_task_status(self, task: Any) -> str:
        """
        Get the status of a Codegen task
        
        Args:
            task: Codegen task object
            
        Returns:
            Task status
        """
        if not self.codegen_agent:
            raise ValueError("Codegen agent not initialized. Call initialize() first.")
            
        # Refresh the task status
        task.refresh()
        
        # Return the status
        return task.status
        
    def get_task_result(self, task: Any) -> Any:
        """
        Get the result of a Codegen task
        
        Args:
            task: Codegen task object
            
        Returns:
            Task result
        """
        if not self.codegen_agent:
            raise ValueError("Codegen agent not initialized. Call initialize() first.")
            
        # Refresh the task status
        task.refresh()
        
        # Return the result
        if task.status == "completed":
            return task.result
        else:
            return None
