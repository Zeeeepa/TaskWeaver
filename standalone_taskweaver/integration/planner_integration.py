#!/usr/bin/env python3
"""
Planner Integration Module

This module provides integration between TaskWeaver's planner and Codegen.
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

class PlannerIntegration:
    """
    Integration between TaskWeaver's planner and Codegen
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
        # Check if the task description contains code-related keywords
        code_keywords = [
            "code", "program", "script", "function", "class", "method",
            "implement", "develop", "create", "write", "generate",
            "python", "javascript", "typescript", "java", "c++", "c#",
            "html", "css", "sql", "api", "endpoint", "server", "client",
            "algorithm", "data structure", "refactor", "optimize", "debug"
        ]
        
        # Check if any of the keywords are in the task description
        for keyword in code_keywords:
            if keyword.lower() in task_description.lower():
                return True
                
        return False
        
    def delegate_to_codegen(self, task_description: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Delegate a code-related task to Codegen
        
        Args:
            task_description: Description of the task
            context: Context information for the task
            
        Returns:
            Dict[str, Any]: Result of the Codegen task
        """
        if not self.codegen_integration.is_initialized:
            return {"success": False, "error": "Codegen integration not initialized"}
            
        try:
            # Create a prompt with the task description and context
            prompt = f"Task: {task_description}\n\n"
            
            # Add context information
            if context:
                prompt += "Context:\n"
                for key, value in context.items():
                    prompt += f"- {key}: {value}\n"
                    
            # Create a Codegen task
            task_id = self.codegen_integration.create_codegen_task(prompt)
            
            if not task_id:
                return {"success": False, "error": "Failed to create Codegen task"}
                
            # Get task status
            task_status = self.codegen_integration.get_task_status(task_id)
            
            if not task_status:
                return {"success": False, "error": f"Failed to get status for task {task_id}"}
                
            # If task is completed, return the result
            if task_status.get("completed", False):
                result = task_status.get("result", {})
                
                return {
                    "success": True,
                    "task_id": task_id,
                    "result": result
                }
            else:
                # Task is still running
                return {
                    "success": True,
                    "task_id": task_id,
                    "status": task_status.get("status", "running"),
                    "message": "Task execution in progress"
                }
        except Exception as e:
            self.logger.error(f"Error delegating task to Codegen: {str(e)}")
            return {"success": False, "error": str(e)}

