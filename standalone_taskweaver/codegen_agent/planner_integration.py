#!/usr/bin/env python3
"""
Planner Integration for Codegen and TaskWeaver

This module provides integration between TaskWeaver's planner and Codegen's
code generation capabilities, allowing the planner to delegate code-related
tasks to Codegen and incorporate the results into its planning process.
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
from standalone_taskweaver.planner.planner import Planner
from standalone_taskweaver.codegen_agent.integration import CodegenIntegration

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("codegen-planner-integration")

class CodegenPlannerIntegration:
    """
    Integration class for Codegen and TaskWeaver's planner
    """
    
    @inject
    def __init__(
        self,
        app: TaskWeaverApp,
        config: AppConfigSource,
        logger: TelemetryLogger,
        codegen_integration: CodegenIntegration,
    ) -> None:
        self.app = app
        self.config = config
        self.logger = logger
        self.codegen_integration = codegen_integration
        
    def is_code_related_task(self, task_description: str) -> bool:
        """
        Determine if a task is code-related and should be delegated to Codegen
        
        Args:
            task_description: Description of the task
            
        Returns:
            bool: True if the task is code-related, False otherwise
        """
        # Keywords that indicate a code-related task
        code_keywords = [
            "code", "implement", "develop", "program", "script",
            "function", "class", "method", "api", "endpoint",
            "refactor", "optimize", "debug", "fix bug", "test",
            "github", "git", "repository", "pull request", "pr",
            "commit", "merge", "branch", "feature", "issue"
        ]
        
        # Check if any of the keywords are in the task description
        return any(keyword in task_description.lower() for keyword in code_keywords)
    
    def delegate_to_codegen(self, task_description: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Delegate a code-related task to Codegen
        
        Args:
            task_description: Description of the task
            context: Context information for the task
            
        Returns:
            Dict[str, Any]: Result of the Codegen task
        """
        try:
            # Create a prompt for Codegen
            prompt = self._create_codegen_prompt(task_description, context)
            
            # Create a Codegen task
            task_id = self.codegen_integration.create_codegen_task(prompt)
            
            if not task_id:
                self.logger.error("Failed to create Codegen task")
                return {"success": False, "error": "Failed to create Codegen task"}
            
            # Wait for the task to complete
            result = self._wait_for_task_completion(task_id)
            
            return result
        except Exception as e:
            self.logger.error(f"Error delegating task to Codegen: {str(e)}")
            return {"success": False, "error": str(e)}
    
    def _create_codegen_prompt(self, task_description: str, context: Dict[str, Any]) -> str:
        """
        Create a prompt for Codegen based on the task description and context
        
        Args:
            task_description: Description of the task
            context: Context information for the task
            
        Returns:
            str: Prompt for Codegen
        """
        # Extract relevant information from context
        repository = context.get("repository", "")
        files = context.get("files", [])
        requirements = context.get("requirements", "")
        
        # Create a prompt template
        prompt_template = f"""
Task: {task_description}

Repository: {repository}

Context:
{json.dumps(context, indent=2)}

Requirements:
{requirements}

Please implement this task by:
1. Analyzing the requirements and context
2. Creating or modifying the necessary code
3. Testing the implementation
4. Creating a pull request with the changes
"""
        
        return prompt_template
    
    def _wait_for_task_completion(self, task_id: str, timeout: int = 3600) -> Dict[str, Any]:
        """
        Wait for a Codegen task to complete
        
        Args:
            task_id: ID of the Codegen task
            timeout: Maximum time to wait in seconds
            
        Returns:
            Dict[str, Any]: Result of the Codegen task
        """
        import time
        
        start_time = time.time()
        while time.time() - start_time < timeout:
            # Get task status
            status = self.codegen_integration.get_task_status(task_id)
            
            if not status:
                self.logger.error(f"Failed to get status for task {task_id}")
                return {"success": False, "error": f"Failed to get status for task {task_id}"}
            
            # Check if task is completed
            if status.get("completed", False):
                return {
                    "success": True,
                    "task_id": task_id,
                    "status": status.get("status"),
                    "result": status.get("result")
                }
            
            # Wait before checking again
            time.sleep(10)
        
        # Timeout
        return {"success": False, "error": f"Task {task_id} timed out"}
    
    def incorporate_codegen_result(self, planner: Planner, task_id: str, result: Dict[str, Any]) -> None:
        """
        Incorporate the result of a Codegen task into the planner
        
        Args:
            planner: TaskWeaver planner
            task_id: ID of the task in the planner
            result: Result of the Codegen task
        """
        try:
            if result.get("success", False):
                # Extract information from the result
                pr_url = self._extract_pr_url(result)
                code_changes = self._extract_code_changes(result)
                
                # Update the task in the planner
                planner.update_task(
                    task_id=task_id,
                    status="completed",
                    result={
                        "pr_url": pr_url,
                        "code_changes": code_changes,
                        "codegen_result": result
                    }
                )
            else:
                # Update the task with the error
                planner.update_task(
                    task_id=task_id,
                    status="failed",
                    result={
                        "error": result.get("error", "Unknown error"),
                        "codegen_result": result
                    }
                )
        except Exception as e:
            self.logger.error(f"Error incorporating Codegen result: {str(e)}")
    
    def _extract_pr_url(self, result: Dict[str, Any]) -> Optional[str]:
        """
        Extract the PR URL from the Codegen result
        
        Args:
            result: Result of the Codegen task
            
        Returns:
            Optional[str]: PR URL if found, None otherwise
        """
        # Try to extract PR URL from the result
        codegen_result = result.get("result", {})
        
        # Check if result is a string (might be JSON)
        if isinstance(codegen_result, str):
            try:
                codegen_result = json.loads(codegen_result)
            except:
                pass
        
        # Try different possible locations for the PR URL
        if isinstance(codegen_result, dict):
            # Check for PR URL in the result
            pr_url = codegen_result.get("pr_url")
            if pr_url:
                return pr_url
            
            # Check for PR URL in the changes
            changes = codegen_result.get("changes", {})
            if isinstance(changes, dict):
                pr_url = changes.get("pr_url")
                if pr_url:
                    return pr_url
        
        return None
    
    def _extract_code_changes(self, result: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Extract code changes from the Codegen result
        
        Args:
            result: Result of the Codegen task
            
        Returns:
            List[Dict[str, Any]]: List of code changes
        """
        # Try to extract code changes from the result
        codegen_result = result.get("result", {})
        
        # Check if result is a string (might be JSON)
        if isinstance(codegen_result, str):
            try:
                codegen_result = json.loads(codegen_result)
            except:
                return []
        
        # Try different possible locations for the code changes
        if isinstance(codegen_result, dict):
            # Check for changes in the result
            changes = codegen_result.get("changes", [])
            if changes:
                return changes if isinstance(changes, list) else []
            
            # Check for files in the result
            files = codegen_result.get("files", [])
            if files:
                return files if isinstance(files, list) else []
        
        return []

