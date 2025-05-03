#!/usr/bin/env python3
"""
Interface Generator for TaskWeaver-Codegen Integration

This module provides functionality for generating interfaces for components
to enable parallel development.
"""

import os
import re
import sys
import json
import logging
from typing import Dict, List, Optional, Any, Union, Tuple, Set

from injector import inject

from standalone_taskweaver.app.app import TaskWeaverApp
from standalone_taskweaver.config.config_mgt import AppConfigSource
from standalone_taskweaver.logging import TelemetryLogger
from standalone_taskweaver.codegen_agent.requirements_manager import AtomicTask

# Import Codegen SDK
try:
    from codegen import Agent
except ImportError:
    print("Codegen SDK not found. Installing...")
    import subprocess
    subprocess.check_call([sys.executable, "-m", "pip", "install", "codegen"])
    from codegen import Agent

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("interface-generator")

class InterfaceGenerator:
    """
    Generates interfaces for components to enable parallel development
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
        self.codegen_agent = None
        
    def initialize(self, org_id: str, token: str) -> None:
        """
        Initialize the Codegen agent
        
        Args:
            org_id: Codegen organization ID
            token: Codegen API token
        """
        self.codegen_agent = Agent(org_id=org_id, token=token)
        logger.info("Initialized Codegen agent")
        
    def generate_interface(self, component_spec: Dict[str, Any]) -> str:
        """
        Generate interface definition for a component
        
        Args:
            component_spec: Component specification
            
        Returns:
            Interface definition
        """
        if not self.codegen_agent:
            raise ValueError("Codegen agent not initialized. Call initialize() first.")
            
        # Create a prompt for the interface
        prompt = self._create_interface_prompt(component_spec)
        
        # Execute the task using the Codegen SDK
        task = self.codegen_agent.run(prompt=prompt)
        
        # Wait for the task to complete
        while task.status not in ["completed", "failed", "cancelled"]:
            # Refresh the task status
            task.refresh()
            
            # Wait a bit before checking again
            import time
            time.sleep(5)
            
        # Return the result
        if task.status == "completed":
            return task.result
        else:
            raise Exception(f"Failed to generate interface: {task.error}")
            
    def _create_interface_prompt(self, component_spec: Dict[str, Any]) -> str:
        """
        Create a prompt for generating an interface
        
        Args:
            component_spec: Component specification
            
        Returns:
            Prompt string
        """
        prompt = f"# Generate Interface for {component_spec.get('name', 'Component')}\n\n"
        
        prompt += "## Component Specification\n\n"
        
        # Add component details
        for key, value in component_spec.items():
            prompt += f"### {key.capitalize()}\n\n{value}\n\n"
            
        prompt += "## Instructions\n\n"
        prompt += "Please generate a clear and comprehensive interface for this component. Include:\n\n"
        prompt += "1. Interface definition with all required methods and properties\n"
        prompt += "2. Method signatures with parameter and return types\n"
        prompt += "3. Detailed documentation for each method and property\n"
        prompt += "4. Type hints and annotations\n"
        prompt += "5. Usage examples\n\n"
        prompt += "The interface should be designed to enable parallel development of dependent components.\n"
        
        return prompt
        
    def create_mock_implementation(self, interface: str) -> str:
        """
        Create mock implementation for an interface
        
        Args:
            interface: Interface definition
            
        Returns:
            Mock implementation
        """
        if not self.codegen_agent:
            raise ValueError("Codegen agent not initialized. Call initialize() first.")
            
        # Create a prompt for the mock implementation
        prompt = self._create_mock_prompt(interface)
        
        # Execute the task using the Codegen SDK
        task = self.codegen_agent.run(prompt=prompt)
        
        # Wait for the task to complete
        while task.status not in ["completed", "failed", "cancelled"]:
            # Refresh the task status
            task.refresh()
            
            # Wait a bit before checking again
            import time
            time.sleep(5)
            
        # Return the result
        if task.status == "completed":
            return task.result
        else:
            raise Exception(f"Failed to create mock implementation: {task.error}")
            
    def _create_mock_prompt(self, interface: str) -> str:
        """
        Create a prompt for generating a mock implementation
        
        Args:
            interface: Interface definition
            
        Returns:
            Prompt string
        """
        prompt = "# Create Mock Implementation for Interface\n\n"
        
        prompt += "## Interface Definition\n\n"
        prompt += f"```\n{interface}\n```\n\n"
        
        prompt += "## Instructions\n\n"
        prompt += "Please create a mock implementation for this interface. The mock implementation should:\n\n"
        prompt += "1. Implement all methods and properties defined in the interface\n"
        prompt += "2. Return sensible default values or test data\n"
        prompt += "3. Include logging to track method calls\n"
        prompt += "4. Be clearly marked as a mock implementation\n"
        prompt += "5. Include usage examples\n\n"
        prompt += "The mock implementation should be usable by dependent components during development.\n"
        
        return prompt
        
    def generate_validation_contract(self, interface: str) -> str:
        """
        Generate validation contract for an interface
        
        Args:
            interface: Interface definition
            
        Returns:
            Validation contract
        """
        if not self.codegen_agent:
            raise ValueError("Codegen agent not initialized. Call initialize() first.")
            
        # Create a prompt for the validation contract
        prompt = self._create_validation_prompt(interface)
        
        # Execute the task using the Codegen SDK
        task = self.codegen_agent.run(prompt=prompt)
        
        # Wait for the task to complete
        while task.status not in ["completed", "failed", "cancelled"]:
            # Refresh the task status
            task.refresh()
            
            # Wait a bit before checking again
            import time
            time.sleep(5)
            
        # Return the result
        if task.status == "completed":
            return task.result
        else:
            raise Exception(f"Failed to generate validation contract: {task.error}")
            
    def _create_validation_prompt(self, interface: str) -> str:
        """
        Create a prompt for generating a validation contract
        
        Args:
            interface: Interface definition
            
        Returns:
            Prompt string
        """
        prompt = "# Generate Validation Contract for Interface\n\n"
        
        prompt += "## Interface Definition\n\n"
        prompt += f"```\n{interface}\n```\n\n"
        
        prompt += "## Instructions\n\n"
        prompt += "Please generate a validation contract for this interface. The validation contract should:\n\n"
        prompt += "1. Define validation rules for all method parameters\n"
        prompt += "2. Define validation rules for all return values\n"
        prompt += "3. Include pre-conditions and post-conditions for each method\n"
        prompt += "4. Provide helper functions for validation\n"
        prompt += "5. Include usage examples\n\n"
        prompt += "The validation contract should help ensure that implementations of the interface behave correctly.\n"
        
        return prompt
        
    def generate_data_format_standards(self, interface: str) -> str:
        """
        Generate data format standards for an interface
        
        Args:
            interface: Interface definition
            
        Returns:
            Data format standards
        """
        if not self.codegen_agent:
            raise ValueError("Codegen agent not initialized. Call initialize() first.")
            
        # Create a prompt for the data format standards
        prompt = self._create_data_format_prompt(interface)
        
        # Execute the task using the Codegen SDK
        task = self.codegen_agent.run(prompt=prompt)
        
        # Wait for the task to complete
        while task.status not in ["completed", "failed", "cancelled"]:
            # Refresh the task status
            task.refresh()
            
            # Wait a bit before checking again
            import time
            time.sleep(5)
            
        # Return the result
        if task.status == "completed":
            return task.result
        else:
            raise Exception(f"Failed to generate data format standards: {task.error}")
            
    def _create_data_format_prompt(self, interface: str) -> str:
        """
        Create a prompt for generating data format standards
        
        Args:
            interface: Interface definition
            
        Returns:
            Prompt string
        """
        prompt = "# Generate Data Format Standards for Interface\n\n"
        
        prompt += "## Interface Definition\n\n"
        prompt += f"```\n{interface}\n```\n\n"
        
        prompt += "## Instructions\n\n"
        prompt += "Please generate data format and structure standards for this interface. The standards should:\n\n"
        prompt += "1. Define the format and structure of all data passed to and from the interface\n"
        prompt += "2. Specify serialization and deserialization rules\n"
        prompt += "3. Define validation rules for data formats\n"
        prompt += "4. Include examples of valid and invalid data\n"
        prompt += "5. Provide helper functions for data conversion\n\n"
        prompt += "The data format standards should help ensure consistent data handling across components.\n"
        
        return prompt
        
    def generate_api_contract(self, interface: str) -> str:
        """
        Generate API contract for an interface
        
        Args:
            interface: Interface definition
            
        Returns:
            API contract
        """
        if not self.codegen_agent:
            raise ValueError("Codegen agent not initialized. Call initialize() first.")
            
        # Create a prompt for the API contract
        prompt = self._create_api_contract_prompt(interface)
        
        # Execute the task using the Codegen SDK
        task = self.codegen_agent.run(prompt=prompt)
        
        # Wait for the task to complete
        while task.status not in ["completed", "failed", "cancelled"]:
            # Refresh the task status
            task.refresh()
            
            # Wait a bit before checking again
            import time
            time.sleep(5)
            
        # Return the result
        if task.status == "completed":
            return task.result
        else:
            raise Exception(f"Failed to generate API contract: {task.error}")
            
    def _create_api_contract_prompt(self, interface: str) -> str:
        """
        Create a prompt for generating an API contract
        
        Args:
            interface: Interface definition
            
        Returns:
            Prompt string
        """
        prompt = "# Generate API Contract for Interface\n\n"
        
        prompt += "## Interface Definition\n\n"
        prompt += f"```\n{interface}\n```\n\n"
        
        prompt += "## Instructions\n\n"
        prompt += "Please generate a comprehensive API contract for this interface. The API contract should:\n\n"
        prompt += "1. Document all methods and properties in the interface\n"
        prompt += "2. Specify the behavior of each method, including edge cases\n"
        prompt += "3. Define error handling and exception behavior\n"
        prompt += "4. Include usage examples for each method\n"
        prompt += "5. Specify performance expectations and constraints\n\n"
        prompt += "The API contract should serve as a complete reference for users of the interface.\n"
        
        return prompt
        
    def extract_interface_from_implementation(self, implementation: str) -> str:
        """
        Extract an interface from an implementation
        
        Args:
            implementation: Implementation code
            
        Returns:
            Interface definition
        """
        if not self.codegen_agent:
            raise ValueError("Codegen agent not initialized. Call initialize() first.")
            
        # Create a prompt for extracting the interface
        prompt = self._create_extraction_prompt(implementation)
        
        # Execute the task using the Codegen SDK
        task = self.codegen_agent.run(prompt=prompt)
        
        # Wait for the task to complete
        while task.status not in ["completed", "failed", "cancelled"]:
            # Refresh the task status
            task.refresh()
            
            # Wait a bit before checking again
            import time
            time.sleep(5)
            
        # Return the result
        if task.status == "completed":
            return task.result
        else:
            raise Exception(f"Failed to extract interface: {task.error}")
            
    def _create_extraction_prompt(self, implementation: str) -> str:
        """
        Create a prompt for extracting an interface
        
        Args:
            implementation: Implementation code
            
        Returns:
            Prompt string
        """
        prompt = "# Extract Interface from Implementation\n\n"
        
        prompt += "## Implementation\n\n"
        prompt += f"```\n{implementation}\n```\n\n"
        
        prompt += "## Instructions\n\n"
        prompt += "Please extract a clean interface from this implementation. The interface should:\n\n"
        prompt += "1. Include all public methods and properties\n"
        prompt += "2. Exclude implementation details\n"
        prompt += "3. Include method signatures with parameter and return types\n"
        prompt += "4. Include documentation for each method and property\n"
        prompt += "5. Follow interface naming conventions\n\n"
        prompt += "The interface should capture the essential functionality without exposing implementation details.\n"
        
        return prompt

