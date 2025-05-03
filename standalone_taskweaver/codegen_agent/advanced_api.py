#!/usr/bin/env python3
"""
Advanced API for Codegen Integration

This module provides a more advanced API surface for Codegen integration,
allowing for more granular control over Codegen's capabilities.
"""

import os
import sys
import json
import logging
import time
from typing import Dict, List, Optional, Any, Union, Tuple

from injector import inject

from standalone_taskweaver.app.app import TaskWeaverApp
from standalone_taskweaver.config.config_mgt import AppConfigSource
from standalone_taskweaver.logging import TelemetryLogger
from standalone_taskweaver.codegen_agent.integration import CodegenIntegration
from standalone_taskweaver.codegen_agent.bidirectional_context import BidirectionalContext

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("codegen-advanced-api")

class CodegenAdvancedAPI:
    """Advanced API for Codegen with specialized methods for code generation, analysis, refactoring, and testing."""
    
    def __init__(self, codegen_token: str, org_id: Optional[str] = None):
        """
        Initialize the Codegen advanced API with authentication credentials.
        
        Args:
            codegen_token: API token for Codegen
            org_id: Optional organization ID
        """
        self.codegen_token = codegen_token
        self.org_id = org_id
        self.logger = logging.getLogger("codegen_advanced_api")
        
        # Initialize the Codegen agent with the new SDK format
        self.codegen_agent = Agent(
            token=codegen_token,
            org_id=org_id
        )
        self.logger.info("Codegen agent initialized successfully")
    
    def run_codegen_task(self, prompt: str) -> Any:
        """
        Run a Codegen task with the given prompt.
        
        Args:
            prompt: The prompt to send to Codegen
            
        Returns:
            The task object
        """
        try:
            task = self.codegen_agent.create_task(prompt=prompt)
            self.logger.info(f"Created task with ID: {task.id}")
            return task
        except Exception as e:
            self.logger.exception(f"Error creating Codegen task: {str(e)}")
            raise
    
    def wait_for_task_completion(self, task: Any, timeout: int = 300) -> Dict[str, Any]:
        """
        Wait for a task to complete with timeout.
        
        Args:
            task: The task object
            timeout: Maximum time to wait in seconds
            
        Returns:
            Dictionary containing the task result or error information
        """
        start_time = time.time()
        while time.time() - start_time < timeout:
            task.refresh()
            if task.status == "completed":
                self.logger.info(f"Task completed successfully")
                return {"success": True, "result": task.result}
            elif task.status in ["failed", "cancelled"]:
                self.logger.error(f"Task failed: {task.status}")
                return {"success": False, "error": f"Task failed: {task.status}"}
            time.sleep(5)
        
        self.logger.error(f"Task timed out after {timeout} seconds")
        return {"success": False, "error": "Task timed out"}
    
    def analyze_code(self, code: str) -> Dict[str, Any]:
        """
        Analyze code to identify potential issues, complexity, and improvement opportunities.
        
        Args:
            code: The code to analyze
            
        Returns:
            Dictionary containing the analysis result or error information
        """
        prompt = f"""
        Analyze the following code and provide insights on:
        1. Code quality and potential issues
        2. Complexity and performance considerations
        3. Improvement opportunities
        4. Best practices adherence
        
        Code to analyze:
        ```
        {code}
        ```
        """
        
        try:
            task = self.run_codegen_task(prompt)
            return self.wait_for_task_completion(task)
        except Exception as e:
            self.logger.exception(f"Error analyzing code: {str(e)}")
            return {"success": False, "error": str(e)}
    
    def generate_tests(self, code: str) -> Dict[str, Any]:
        """
        Generate comprehensive tests for the provided code.
        
        Args:
            code: The code to generate tests for
            
        Returns:
            Dictionary containing the generated tests or error information
        """
        prompt = f"""
        Generate comprehensive tests for the following code:
        ```
        {code}
        ```
        
        Include tests for:
        1. Normal operation
        2. Edge cases
        3. Error handling
        4. Performance considerations
        
        Return the tests in a format appropriate for the language of the provided code.
        """
        
        try:
            task = self.run_codegen_task(prompt)
            return self.wait_for_task_completion(task)
        except Exception as e:
            self.logger.exception(f"Error generating tests: {str(e)}")
            return {"success": False, "error": str(e)}
    
    def refactor_code(self, code: str, requirements: Optional[str] = None) -> Dict[str, Any]:
        """
        Refactor code to improve quality, readability, and performance.
        
        Args:
            code: The code to refactor
            requirements: Optional requirements for the refactoring
            
        Returns:
            Dictionary containing the refactored code or error information
        """
        prompt = f"""
        Refactor the following code to improve quality, readability, and performance:
        ```
        {code}
        ```
        
        {f"Requirements for the refactoring:\n{requirements}" if requirements else ""}
        
        Return the refactored code with explanations of the improvements made.
        """
        
        try:
            task = self.run_codegen_task(prompt)
            return self.wait_for_task_completion(task)
        except Exception as e:
            self.logger.exception(f"Error refactoring code: {str(e)}")
            return {"success": False, "error": str(e)}
    
    def generate_documentation(self, code: str) -> Dict[str, Any]:
        """
        Generate comprehensive documentation for the provided code.
        
        Args:
            code: The code to document
            
        Returns:
            Dictionary containing the generated documentation or error information
        """
        prompt = f"""
        Generate comprehensive documentation for the following code:
        ```
        {code}
        ```
        
        Include:
        1. Overview of functionality
        2. API documentation
        3. Usage examples
        4. Dependencies and requirements
        
        Return the documentation in markdown format.
        """
        
        try:
            task = self.run_codegen_task(prompt)
            return self.wait_for_task_completion(task)
        except Exception as e:
            self.logger.exception(f"Error generating documentation: {str(e)}")
            return {"success": False, "error": str(e)}
