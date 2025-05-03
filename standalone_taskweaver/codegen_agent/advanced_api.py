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
    
    def generate_code(self, prompt: str, language: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Generate code using Codegen
        
        Args:
            prompt: Prompt for code generation
            language: Programming language
            context: Optional context information
            
        Returns:
            Dict[str, Any]: Generated code
        """
        try:
            # Create a prompt for Codegen
            codegen_prompt = self._create_code_generation_prompt(prompt, language, context)
            
            # Create a Codegen task
            task_id = self.codegen_integration.create_codegen_task(codegen_prompt)
            
            if not task_id:
                self.logger.error("Failed to create Codegen task for code generation")
                return {"success": False, "error": "Failed to create Codegen task"}
            
            # Wait for the task to complete
            result = self._wait_for_task_completion(task_id)
            
            # Extract code from the result
            code = self._extract_code_from_result(result, language)
            
            return {
                "success": True,
                "code": code,
                "task_id": task_id,
                "result": result
            }
        except Exception as e:
            self.logger.error(f"Error generating code: {str(e)}")
            return {"success": False, "error": str(e)}
    
    def _create_code_generation_prompt(self, prompt: str, language: str, context: Optional[Dict[str, Any]] = None) -> str:
        """
        Create a prompt for code generation
        
        Args:
            prompt: Prompt for code generation
            language: Programming language
            context: Optional context information
            
        Returns:
            str: Prompt for Codegen
        """
        # Get context information
        if context is None:
            context = self.context_manager.export_context_for_codegen()
        
        # Create a prompt template
        prompt_template = f"""
Generate code in {language} for the following task:

{prompt}

Context:
{json.dumps(context, indent=2) if context else "No context provided"}

Please provide only the code without any explanations or comments.
"""
        
        return prompt_template
    
    def _extract_code_from_result(self, result: Dict[str, Any], language: str) -> str:
        """
        Extract code from the Codegen result
        
        Args:
            result: Result of the Codegen task
            language: Programming language
            
        Returns:
            str: Extracted code
        """
        # Try to extract code from the result
        codegen_result = result.get("result", {})
        
        # Check if result is a string (might be JSON)
        if isinstance(codegen_result, str):
            try:
                codegen_result = json.loads(codegen_result)
            except:
                # If it's not JSON, it might be the code directly
                return codegen_result
        
        # Try different possible locations for the code
        if isinstance(codegen_result, dict):
            # Check for code in the result
            code = codegen_result.get("code")
            if code:
                return code
            
            # Check for files in the result
            files = codegen_result.get("files", [])
            if files and isinstance(files, list):
                for file in files:
                    if isinstance(file, dict) and file.get("language", "").lower() == language.lower():
                        return file.get("content", "")
        
        # If we couldn't extract the code, return the entire result
        return str(codegen_result)
    
    def analyze_code(self, code: str, language: str) -> Dict[str, Any]:
        """
        Analyze code using Codegen
        
        Args:
            code: Code to analyze
            language: Programming language
            
        Returns:
            Dict[str, Any]: Analysis result
        """
        try:
            # Create a prompt for Codegen
            codegen_prompt = self._create_code_analysis_prompt(code, language)
            
            # Create a Codegen task
            task_id = self.codegen_integration.create_codegen_task(codegen_prompt)
            
            if not task_id:
                self.logger.error("Failed to create Codegen task for code analysis")
                return {"success": False, "error": "Failed to create Codegen task"}
            
            # Wait for the task to complete
            result = self._wait_for_task_completion(task_id)
            
            # Extract analysis from the result
            analysis = self._extract_analysis_from_result(result)
            
            return {
                "success": True,
                "analysis": analysis,
                "task_id": task_id,
                "result": result
            }
        except Exception as e:
            self.logger.error(f"Error analyzing code: {str(e)}")
            return {"success": False, "error": str(e)}
    
    def _create_code_analysis_prompt(self, code: str, language: str) -> str:
        """
        Create a prompt for code analysis
        
        Args:
            code: Code to analyze
            language: Programming language
            
        Returns:
            str: Prompt for Codegen
        """
        # Create a prompt template
        prompt_template = f"""
Analyze the following {language} code:

```{language}
{code}
```

Please provide a detailed analysis including:
1. Code quality assessment
2. Potential bugs or issues
3. Performance considerations
4. Security vulnerabilities
5. Suggestions for improvement

Format the analysis as JSON with the following structure:
{{
  "quality": "assessment of code quality",
  "bugs": ["list of potential bugs"],
  "performance": ["performance considerations"],
  "security": ["security vulnerabilities"],
  "suggestions": ["suggestions for improvement"]
}}
"""
        
        return prompt_template
    
    def _extract_analysis_from_result(self, result: Dict[str, Any]) -> Dict[str, Any]:
        """
        Extract analysis from the Codegen result
        
        Args:
            result: Result of the Codegen task
            
        Returns:
            Dict[str, Any]: Extracted analysis
        """
        # Try to extract analysis from the result
        codegen_result = result.get("result", {})
        
        # Check if result is a string (might be JSON)
        if isinstance(codegen_result, str):
            try:
                codegen_result = json.loads(codegen_result)
                return codegen_result
            except:
                # If it's not JSON, return a simple analysis
                return {
                    "analysis": codegen_result
                }
        
        # If result is already a dict, return it
        if isinstance(codegen_result, dict):
            return codegen_result
        
        # If we couldn't extract the analysis, return the entire result
        return {
            "analysis": str(codegen_result)
        }
    
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
        try:
            # Create a prompt for Codegen
            codegen_prompt = self._create_code_refactoring_prompt(code, language, instructions)
            
            # Create a Codegen task
            task_id = self.codegen_integration.create_codegen_task(codegen_prompt)
            
            if not task_id:
                self.logger.error("Failed to create Codegen task for code refactoring")
                return {"success": False, "error": "Failed to create Codegen task"}
            
            # Wait for the task to complete
            result = self._wait_for_task_completion(task_id)
            
            # Extract refactored code from the result
            refactored_code = self._extract_code_from_result(result, language)
            
            return {
                "success": True,
                "refactored_code": refactored_code,
                "task_id": task_id,
                "result": result
            }
        except Exception as e:
            self.logger.error(f"Error refactoring code: {str(e)}")
            return {"success": False, "error": str(e)}
    
    def _create_code_refactoring_prompt(self, code: str, language: str, instructions: str) -> str:
        """
        Create a prompt for code refactoring
        
        Args:
            code: Code to refactor
            language: Programming language
            instructions: Refactoring instructions
            
        Returns:
            str: Prompt for Codegen
        """
        # Create a prompt template
        prompt_template = f"""
Refactor the following {language} code according to these instructions:

Instructions:
{instructions}

Original code:
```{language}
{code}
```

Please provide only the refactored code without any explanations or comments.
"""
        
        return prompt_template
    
    def generate_tests(self, code: str, language: str) -> Dict[str, Any]:
        """
        Generate tests for code using Codegen
        
        Args:
            code: Code to generate tests for
            language: Programming language
            
        Returns:
            Dict[str, Any]: Generated tests
        """
        try:
            # Create a prompt for Codegen
            codegen_prompt = self._create_test_generation_prompt(code, language)
            
            # Create a Codegen task
            task_id = self.codegen_integration.create_codegen_task(codegen_prompt)
            
            if not task_id:
                self.logger.error("Failed to create Codegen task for test generation")
                return {"success": False, "error": "Failed to create Codegen task"}
            
            # Wait for the task to complete
            result = self._wait_for_task_completion(task_id)
            
            # Extract tests from the result
            tests = self._extract_code_from_result(result, language)
            
            return {
                "success": True,
                "tests": tests,
                "task_id": task_id,
                "result": result
            }
        except Exception as e:
            self.logger.error(f"Error generating tests: {str(e)}")
            return {"success": False, "error": str(e)}
    
    def _create_test_generation_prompt(self, code: str, language: str) -> str:
        """
        Create a prompt for test generation
        
        Args:
            code: Code to generate tests for
            language: Programming language
            
        Returns:
            str: Prompt for Codegen
        """
        # Create a prompt template
        prompt_template = f"""
Generate comprehensive tests for the following {language} code:

```{language}
{code}
```

Please provide tests that cover:
1. Normal operation
2. Edge cases
3. Error handling

Use the appropriate testing framework for {language}.
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

