#!/usr/bin/env python3
"""
Advanced API Module

This module provides advanced API functionality for Codegen integration.
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
from standalone_taskweaver.integration.bidirectional_context import BidirectionalContext

class AdvancedAPI:
    """
    Advanced API for Codegen integration
    """
    
    @inject
    def __init__(
        self,
        app: TaskWeaverApp,
        config: AppConfigSource,
        logger: TelemetryLogger,
        codegen_integration: CodegenIntegration,
        context_manager: BidirectionalContext,
    ) -> None:
        self.app = app
        self.config = config
        self.logger = logger
        self.codegen_integration = codegen_integration
        self.context_manager = context_manager
        
    def generate_code(self, prompt: str, language: str) -> Dict[str, Any]:
        """
        Generate code using Codegen
        
        Args:
            prompt: Prompt for code generation
            language: Programming language
            
        Returns:
            Dict[str, Any]: Generated code
        """
        if not self.codegen_integration.is_initialized:
            return {"success": False, "error": "Codegen integration not initialized"}
            
        try:
            # Create a task for code generation
            task_id = self.codegen_integration.create_codegen_task(
                f"Generate {language} code for: {prompt}"
            )
            
            if not task_id:
                return {"success": False, "error": "Failed to create code generation task"}
                
            # Get task status
            task_status = self.codegen_integration.get_task_status(task_id)
            
            if not task_status:
                return {"success": False, "error": f"Failed to get status for task {task_id}"}
                
            # If task is completed, return the result
            if task_status.get("completed", False):
                result = task_status.get("result", {})
                
                # Add to context
                self.context_manager.update_codegen_context({
                    "variables": {
                        f"generated_code_{language}": result
                    }
                })
                
                return {
                    "success": True,
                    "task_id": task_id,
                    "code": result,
                    "language": language
                }
            else:
                # Task is still running
                return {
                    "success": True,
                    "task_id": task_id,
                    "status": task_status.get("status", "running"),
                    "message": "Code generation in progress"
                }
        except Exception as e:
            self.logger.error(f"Error generating code: {str(e)}")
            return {"success": False, "error": str(e)}
            
    def analyze_code(self, code: str, language: str) -> Dict[str, Any]:
        """
        Analyze code using Codegen
        
        Args:
            code: Code to analyze
            language: Programming language
            
        Returns:
            Dict[str, Any]: Analysis result
        """
        if not self.codegen_integration.is_initialized:
            return {"success": False, "error": "Codegen integration not initialized"}
            
        try:
            # Create a task for code analysis
            task_id = self.codegen_integration.create_codegen_task(
                f"Analyze the following {language} code:\n\n```{language}\n{code}\n```"
            )
            
            if not task_id:
                return {"success": False, "error": "Failed to create code analysis task"}
                
            # Get task status
            task_status = self.codegen_integration.get_task_status(task_id)
            
            if not task_status:
                return {"success": False, "error": f"Failed to get status for task {task_id}"}
                
            # If task is completed, return the result
            if task_status.get("completed", False):
                result = task_status.get("result", {})
                
                # Add to context
                self.context_manager.update_codegen_context({
                    "variables": {
                        f"analyzed_code_{language}": result
                    }
                })
                
                return {
                    "success": True,
                    "task_id": task_id,
                    "analysis": result,
                    "language": language
                }
            else:
                # Task is still running
                return {
                    "success": True,
                    "task_id": task_id,
                    "status": task_status.get("status", "running"),
                    "message": "Code analysis in progress"
                }
        except Exception as e:
            self.logger.error(f"Error analyzing code: {str(e)}")
            return {"success": False, "error": str(e)}
            
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
        if not self.codegen_integration.is_initialized:
            return {"success": False, "error": "Codegen integration not initialized"}
            
        try:
            # Create a task for code refactoring
            task_id = self.codegen_integration.create_codegen_task(
                f"Refactor the following {language} code according to these instructions: {instructions}\n\n```{language}\n{code}\n```"
            )
            
            if not task_id:
                return {"success": False, "error": "Failed to create code refactoring task"}
                
            # Get task status
            task_status = self.codegen_integration.get_task_status(task_id)
            
            if not task_status:
                return {"success": False, "error": f"Failed to get status for task {task_id}"}
                
            # If task is completed, return the result
            if task_status.get("completed", False):
                result = task_status.get("result", {})
                
                # Add to context
                self.context_manager.update_codegen_context({
                    "variables": {
                        f"refactored_code_{language}": result
                    }
                })
                
                return {
                    "success": True,
                    "task_id": task_id,
                    "code": result,
                    "language": language
                }
            else:
                # Task is still running
                return {
                    "success": True,
                    "task_id": task_id,
                    "status": task_status.get("status", "running"),
                    "message": "Code refactoring in progress"
                }
        except Exception as e:
            self.logger.error(f"Error refactoring code: {str(e)}")
            return {"success": False, "error": str(e)}
            
    def generate_tests(self, code: str, language: str) -> Dict[str, Any]:
        """
        Generate tests for code using Codegen
        
        Args:
            code: Code to generate tests for
            language: Programming language
            
        Returns:
            Dict[str, Any]: Generated tests
        """
        if not self.codegen_integration.is_initialized:
            return {"success": False, "error": "Codegen integration not initialized"}
            
        try:
            # Create a task for test generation
            task_id = self.codegen_integration.create_codegen_task(
                f"Generate tests for the following {language} code:\n\n```{language}\n{code}\n```"
            )
            
            if not task_id:
                return {"success": False, "error": "Failed to create test generation task"}
                
            # Get task status
            task_status = self.codegen_integration.get_task_status(task_id)
            
            if not task_status:
                return {"success": False, "error": f"Failed to get status for task {task_id}"}
                
            # If task is completed, return the result
            if task_status.get("completed", False):
                result = task_status.get("result", {})
                
                # Add to context
                self.context_manager.update_codegen_context({
                    "variables": {
                        f"generated_tests_{language}": result
                    }
                })
                
                return {
                    "success": True,
                    "task_id": task_id,
                    "tests": result,
                    "language": language
                }
            else:
                # Task is still running
                return {
                    "success": True,
                    "task_id": task_id,
                    "status": task_status.get("status", "running"),
                    "message": "Test generation in progress"
                }
        except Exception as e:
            self.logger.error(f"Error generating tests: {str(e)}")
            return {"success": False, "error": str(e)}

