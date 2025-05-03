#!/usr/bin/env python3
"""
Codegen integration module for TaskWeaver.
"""

import os
import requests
from typing import Dict, Any, Optional, List


class CodegenIntegration:
    """
    Integration with Codegen API.
    """

    def __init__(self, api_key: Optional[str] = None, base_url: Optional[str] = None):
        """
        Initialize the Codegen integration.

        Args:
            api_key: Optional API key for Codegen. If not provided, will try to get from environment.
            base_url: Optional base URL for Codegen API. If not provided, will use default.
        """
        self.api_key = api_key or os.environ.get("CODEGEN_API_KEY")
        self.base_url = base_url or os.environ.get("CODEGEN_API_ENDPOINT", "https://api.codegen.sh")
        self.initialized = False

    def initialize(self) -> None:
        """
        Initialize the Codegen integration.
        """
        if not self.api_key:
            raise ValueError("Codegen API key is required. Please set CODEGEN_API_KEY environment variable.")
        
        self.initialized = True

    def generate_code(self, prompt: str, language: str = "python") -> str:
        """
        Generate code using Codegen API.

        Args:
            prompt: The prompt to generate code from.
            language: The programming language to generate code in.

        Returns:
            The generated code.
        """
        if not self.initialized:
            self.initialize()
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        data = {
            "prompt": prompt,
            "language": language
        }
        
        response = requests.post(f"{self.base_url}/generate", headers=headers, json=data)
        response.raise_for_status()
        
        return response.json().get("code", "")

    def analyze_code(self, code: str, language: str = "python") -> Dict[str, Any]:
        """
        Analyze code using Codegen API.

        Args:
            code: The code to analyze.
            language: The programming language of the code.

        Returns:
            Analysis results.
        """
        if not self.initialized:
            self.initialize()
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        data = {
            "code": code,
            "language": language
        }
        
        response = requests.post(f"{self.base_url}/analyze", headers=headers, json=data)
        response.raise_for_status()
        
        return response.json()

    def refactor_code(self, code: str, instructions: str, language: str = "python") -> str:
        """
        Refactor code using Codegen API.

        Args:
            code: The code to refactor.
            instructions: Instructions for refactoring.
            language: The programming language of the code.

        Returns:
            The refactored code.
        """
        if not self.initialized:
            self.initialize()
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        data = {
            "code": code,
            "instructions": instructions,
            "language": language
        }
        
        response = requests.post(f"{self.base_url}/refactor", headers=headers, json=data)
        response.raise_for_status()
        
        return response.json().get("code", "")

    def generate_tests(self, code: str, language: str = "python") -> str:
        """
        Generate tests for code using Codegen API.

        Args:
            code: The code to generate tests for.
            language: The programming language of the code.

        Returns:
            The generated tests.
        """
        if not self.initialized:
            self.initialize()
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        data = {
            "code": code,
            "language": language
        }
        
        response = requests.post(f"{self.base_url}/generate-tests", headers=headers, json=data)
        response.raise_for_status()
        
        return response.json().get("tests", "")

