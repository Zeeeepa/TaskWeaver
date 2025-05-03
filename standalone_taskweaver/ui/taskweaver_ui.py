#!/usr/bin/env python3
"""
TaskWeaver UI class for Codegen integration
"""

import os
import json
import logging
from typing import Dict, List, Optional, Any, Union, Tuple

from injector import inject

from standalone_taskweaver.app.app import TaskWeaverApp
from standalone_taskweaver.config.config_mgt import AppConfigSource
from standalone_taskweaver.logging import TelemetryLogger
from standalone_taskweaver.integration.codegen_integration import CodegenIntegration
from standalone_taskweaver.integration.bidirectional_context import BidirectionalContext
from standalone_taskweaver.integration.advanced_api import AdvancedAPI
from standalone_taskweaver.integration.planner_integration import PlannerIntegration
from standalone_taskweaver.integration.requirements_manager import RequirementsManager

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("taskweaver-ui")

class TaskWeaverUI:
    """
    TaskWeaver UI class with enhanced Codegen integration
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
        self.codegen_integration = None
        self.context_manager = None
        self.advanced_api = None
        self.planner_integration = None
        self.requirements_manager = None
        self.is_initialized = False
        
        # OpenAI settings
        self.openai_settings = {
            "api_key": os.environ.get("OPENAI_API_KEY", ""),
            "api_base": os.environ.get("OPENAI_API_BASE", "https://api.openai.com/v1"),
            "model": os.environ.get("OPENAI_MODEL", "gpt-4")
        }
        
    def set_openai_settings(self, 
                           api_key: str,
                           api_base: Optional[str] = None,
                           model: Optional[str] = None) -> bool:
        """
        Set OpenAI API settings
        
        Args:
            api_key: OpenAI API key
            api_base: OpenAI API base URL (optional)
            model: OpenAI model name (optional)
            
        Returns:
            bool: True if settings were updated successfully
        """
        try:
            # Update settings
            self.openai_settings["api_key"] = api_key
            
            if api_base:
                self.openai_settings["api_base"] = api_base
                
            if model:
                self.openai_settings["model"] = model
                
            # Set environment variables
            os.environ["OPENAI_API_KEY"] = api_key
            
            if api_base:
                os.environ["OPENAI_API_BASE"] = api_base
                
            if model:
                os.environ["OPENAI_MODEL"] = model
                
            self.logger.info("OpenAI settings updated successfully")
            return True
        except Exception as e:
            self.logger.error(f"Error updating OpenAI settings: {str(e)}")
            return False
        
    def initialize_integration(self, 
                              github_token: str,
                              codegen_token: str,
                              ngrok_token: str,
                              codegen_org_id: str,
                              repo_name: Optional[str] = None) -> bool:
        """
        Initialize Codegen integration with API credentials
        
        Args:
            github_token: GitHub API token
            codegen_token: Codegen API token
            ngrok_token: ngrok API token
            codegen_org_id: Codegen organization ID
            repo_name: Optional repository name
            
        Returns:
            bool: True if initialization was successful, False otherwise
        """
        try:
            # Initialize Codegen integration
            self.codegen_integration = CodegenIntegration(self.app, self.config, self.logger)
            success = self.codegen_integration.initialize(
                github_token=github_token,
                codegen_token=codegen_token,
                ngrok_token=ngrok_token,
                codegen_org_id=codegen_org_id,
                repo_name=repo_name
            )
            
            if success:
                # Initialize context manager
                self.context_manager = BidirectionalContext(
                    self.app,
                    self.config,
                    self.logger,
                    self.codegen_integration
                )
                self.context_manager.initialize()
                
                # Initialize advanced API
                self.advanced_api = AdvancedAPI(
                    self.app,
                    self.config,
                    self.logger,
                    self.codegen_integration,
                    self.context_manager
                )
                
                # Initialize planner integration
                self.planner_integration = PlannerIntegration(
                    self.app,
                    self.config,
                    self.logger,
                    self.codegen_integration
                )
                
                # Initialize requirements manager
                self.requirements_manager = RequirementsManager(
                    self.app,
                    self.config,
                    self.logger
                )
                
                self.is_initialized = True
            
            return success
        except Exception as e:
            self.logger.error(f"Error initializing Codegen integration: {str(e)}")
            return False
            
    def get_github_repos(self) -> List[str]:
        """
        Get list of GitHub repositories
        
        Returns:
            List[str]: List of GitHub repositories
        """
        if not self.is_initialized or not self.codegen_integration:
            return []
                
        return self.codegen_integration.get_repositories()
        
    def set_repository(self, repo_name: str) -> bool:
        """
        Set the active GitHub repository
        
        Args:
            repo_name: GitHub repository name
            
        Returns:
            bool: True if successful, False otherwise
        """
        if not self.is_initialized or not self.codegen_integration:
            return False
                
        return self.codegen_integration.set_repository(repo_name)
        
    def create_codegen_task(self, prompt: str, repo_name: Optional[str] = None) -> Dict[str, Any]:
        """
        Create a Codegen task
        
        Args:
            prompt: Task prompt
            repo_name: Optional repository name
            
        Returns:
            Dict[str, Any]: Task information
        """
        if not self.is_initialized or not self.codegen_integration:
            return {"success": False, "error": "Codegen integration not initialized"}
                
        task_id = self.codegen_integration.create_codegen_task(prompt, repo_name)
        
        if task_id:
            return {
                "success": True,
                "task_id": task_id,
                "prompt": prompt,
                "repo_name": repo_name
            }
        else:
            return {"success": False, "error": "Failed to create task"}
        
    def get_task_status(self, task_id: str) -> Dict[str, Any]:
        """
        Get the status of a Codegen task
        
        Args:
            task_id: Task ID
            
        Returns:
            Dict[str, Any]: Task status
        """
        if not self.is_initialized or not self.codegen_integration:
            return {"success": False, "error": "Codegen integration not initialized"}
                
        status = self.codegen_integration.get_task_status(task_id)
        
        if status:
            return {
                "success": True,
                "task": status
            }
        else:
            return {"success": False, "error": f"Failed to get status for task {task_id}"}
        
    def list_tasks(self) -> Dict[str, Any]:
        """
        List all tasks
        
        Returns:
            Dict[str, Any]: List of tasks
        """
        if not self.is_initialized or not self.codegen_integration:
            return {"success": False, "error": "Codegen integration not initialized", "tasks": []}
        
        # This is a placeholder since the current integration doesn't support listing tasks
        # In a real implementation, you would call the Codegen API to get a list of tasks
        return {"success": True, "tasks": []}
        
    def create_requirements_document(self, requirements: str) -> Dict[str, Any]:
        """
        Create or update a REQUIREMENTS.md file in the repository
        
        Args:
            requirements: Requirements content
            
        Returns:
            Dict[str, Any]: Result of the operation
        """
        if not self.is_initialized or not self.codegen_integration:
            return {"success": False, "error": "Codegen integration not initialized"}
        
        if not self.requirements_manager:
            return {"success": False, "error": "Requirements manager not initialized"}
                
        # Parse requirements
        parsed_requirements = self.requirements_manager.parse_requirements(requirements)
        
        # Generate Markdown
        markdown = self.requirements_manager.generate_requirements_markdown(parsed_requirements)
        
        # Create or update the file in the repository
        success, error = self.codegen_integration.create_requirements_document(markdown)
        return {"success": success, "error": error}
        
    def start_workflow(self) -> Dict[str, Any]:
        """
        Start the Codegen workflow
        
        Returns:
            Dict[str, Any]: Result of the operation
        """
        if not self.is_initialized or not self.codegen_integration:
            return {"success": False, "error": "Codegen integration not initialized"}
                
        success = self.codegen_integration.start_workflow()
        return {"success": success}
        
    def stop_workflow(self) -> Dict[str, Any]:
        """
        Stop the Codegen workflow
        
        Returns:
            Dict[str, Any]: Result of the operation
        """
        if not self.is_initialized or not self.codegen_integration:
            return {"success": False, "error": "Codegen integration not initialized"}
                
        success = self.codegen_integration.stop_workflow()
        return {"success": success}
        
    def get_integration_status(self) -> Dict[str, Any]:
        """
        Get the status of the Codegen integration
        
        Returns:
            Dict[str, Any]: Integration status
        """
        if not self.is_initialized or not self.codegen_integration:
            return {
                "success": True,
                "initialized": False,
                "github_connected": False,
                "codegen_connected": False,
                "ngrok_connected": False,
                "workflow_manager": False,
                "repository": None,
                "advanced_api": False,
                "planner_integration": False,
                "context_manager": False,
                "requirements_manager": False
            }
            
        status = self.codegen_integration.get_status()
        status["success"] = True
        status["initialized"] = self.is_initialized
        status["advanced_api"] = self.advanced_api is not None
        status["planner_integration"] = self.planner_integration is not None
        status["context_manager"] = self.context_manager is not None
        status["requirements_manager"] = self.requirements_manager is not None
        
        return status
    
    # Advanced API methods
    
    def generate_code(self, prompt: str, language: str) -> Dict[str, Any]:
        """
        Generate code using Codegen
        
        Args:
            prompt: Prompt for code generation
            language: Programming language
            
        Returns:
            Dict[str, Any]: Generated code
        """
        if not self.is_initialized or not self.advanced_api:
            return {"success": False, "error": "Advanced API not initialized"}
        
        return self.advanced_api.generate_code(prompt, language)
    
    def analyze_code(self, code: str, language: str) -> Dict[str, Any]:
        """
        Analyze code using Codegen
        
        Args:
            code: Code to analyze
            language: Programming language
            
        Returns:
            Dict[str, Any]: Analysis result
        """
        if not self.is_initialized or not self.advanced_api:
            return {"success": False, "error": "Advanced API not initialized"}
        
        return self.advanced_api.analyze_code(code, language)
    
    def refactor_code(self, code: str, language: str, instructions: str) -> Dict[str, Any]:
        """
        Refactor code using Codegen
        
        Args:
            code: Code to refactor
            language: Programming language
            instructions: Refactoring instructions
            
        Returns:
            Dict[str, Any]: Refactored code
        """
        if not self.is_initialized or not self.advanced_api:
            return {"success": False, "error": "Advanced API not initialized"}
        
        return self.advanced_api.refactor_code(code, language, instructions)
    
    def generate_tests(self, code: str, language: str) -> Dict[str, Any]:
        """
        Generate tests for code using Codegen
        
        Args:
            code: Code to generate tests for
            language: Programming language
            
        Returns:
            Dict[str, Any]: Generated tests
        """
        if not self.is_initialized or not self.advanced_api:
            return {"success": False, "error": "Advanced API not initialized"}
        
        return self.advanced_api.generate_tests(code, language)
    
    # Planner integration methods
    
    def is_code_related_task(self, task_description: str) -> Dict[str, Any]:
        """
        Determine if a task is code-related and should be delegated to Codegen
        
        Args:
            task_description: Description of the task
            
        Returns:
            Dict[str, Any]: Result of the operation
        """
        if not self.is_initialized or not self.planner_integration:
            return {"success": False, "error": "Planner integration not initialized"}
        
        is_code_related = self.planner_integration.is_code_related_task(task_description)
        return {"success": True, "is_code_related": is_code_related}
    
    def delegate_to_codegen(self, task_description: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Delegate a code-related task to Codegen
        
        Args:
            task_description: Description of the task
            context: Context information for the task
            
        Returns:
            Dict[str, Any]: Result of the Codegen task
        """
        if not self.is_initialized or not self.planner_integration:
            return {"success": False, "error": "Planner integration not initialized"}
        
        return self.planner_integration.delegate_to_codegen(task_description, context)
    
    # Context manager methods
    
    def get_shared_context(self) -> Dict[str, Any]:
        """
        Get shared context between TaskWeaver and Codegen
        
        Returns:
            Dict[str, Any]: Shared context
        """
        if not self.is_initialized or not self.context_manager:
            return {"success": True, "context": {}}
            
        return {"success": True, "context": self.context_manager.get_shared_context()}
    
    def update_taskweaver_context(self, context_update: Dict[str, Any]) -> Dict[str, Any]:
        """
        Update TaskWeaver context
        
        Args:
            context_update: Context update from TaskWeaver
            
        Returns:
            Dict[str, Any]: Result of the operation
        """
        if not self.is_initialized or not self.context_manager:
            return {"success": False, "error": "Context manager not initialized"}
            
        try:
            self.context_manager.update_taskweaver_context(context_update)
            return {"success": True}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def update_codegen_context(self, context_update: Dict[str, Any]) -> Dict[str, Any]:
        """
        Update Codegen context
        
        Args:
            context_update: Context update from Codegen
            
        Returns:
            Dict[str, Any]: Result of the operation
        """
        if not self.is_initialized or not self.context_manager:
            return {"success": False, "error": "Context manager not initialized"}
            
        try:
            self.context_manager.update_codegen_context(context_update)
            return {"success": True}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def add_issue_to_context(self, issue_number: int) -> Dict[str, Any]:
        """
        Add a GitHub issue to the context
        
        Args:
            issue_number: GitHub issue number
            
        Returns:
            Dict[str, Any]: Result of the operation
        """
        if not self.is_initialized or not self.context_manager:
            return {"success": False, "error": "Context manager not initialized"}
            
        try:
            self.context_manager.add_issue_to_context(issue_number)
            return {"success": True}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def add_pr_to_context(self, pr_number: int) -> Dict[str, Any]:
        """
        Add a GitHub pull request to the context
        
        Args:
            pr_number: GitHub pull request number
            
        Returns:
            Dict[str, Any]: Result of the operation
        """
        if not self.is_initialized or not self.context_manager:
            return {"success": False, "error": "Context manager not initialized"}
            
        try:
            self.context_manager.add_pr_to_context(pr_number)
            return {"success": True}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def add_file_to_context(self, file_path: str) -> Dict[str, Any]:
        """
        Add a file to the context
        
        Args:
            file_path: Path to the file
            
        Returns:
            Dict[str, Any]: Result of the operation
        """
        if not self.is_initialized or not self.context_manager:
            return {"success": False, "error": "Context manager not initialized"}
            
        try:
            self.context_manager.add_file_to_context(file_path)
            return {"success": True}
        except Exception as e:
            return {"success": False, "error": str(e)}
