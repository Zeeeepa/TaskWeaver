#!/usr/bin/env python3
"""
Weaver Integration for Codegen Agent

This module provides the integration between TaskWeaver's weaver component
and the Codegen agent, allowing the weaver to call the Codegen agent for
executing deployment steps.
"""

import os
import sys
import json
import logging
import asyncio
from typing import Dict, List, Optional, Any, Union, Tuple, Set

from injector import inject

from standalone_taskweaver.app.app import TaskWeaverApp
from standalone_taskweaver.config.config_mgt import AppConfigSource
from standalone_taskweaver.logging import TelemetryLogger
from standalone_taskweaver.memory import Memory
from standalone_taskweaver.codegen_agent.codegen_agent import CodegenAgent, CodegenAgentStatus
from standalone_taskweaver.codegen_agent.requirements_manager import RequirementsManager, AtomicTask
from standalone_taskweaver.codegen_agent.concurrent_execution import TaskStatus, TaskResult
from standalone_taskweaver.codegen_agent.utils import safe_execute, validate_required_params, compress_context

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("weaver-codegen-integration")

class CodegenWeaverIntegration:
    """
    Integration between TaskWeaver's weaver component and the Codegen agent
    
    This class provides a bridge between TaskWeaver's weaver component and the Codegen agent,
    allowing the weaver to call the Codegen agent for executing deployment steps.
    """
    
    @inject
    def __init__(
        self,
        app: TaskWeaverApp,
        config: AppConfigSource,
        logger: TelemetryLogger,
        memory: Optional[Memory] = None,
        codegen_agent: Optional[CodegenAgent] = None,
    ) -> None:
        self.app = app
        self.config = config
        self.logger = logger
        self.memory = memory or Memory()
        self.codegen_agent = codegen_agent
        
        # Initialization status
        self.is_initialized = False
        
        # Project context
        self.current_project = None
        
        # Deployment steps
        self.deployment_steps = []
        self.step_results = {}
        
        # Maximum number of stored results to prevent memory leaks
        self.max_stored_results = 100
        
    def initialize(self, codegen_token: str) -> bool:
        """
        Initialize the Codegen agent with the provided token
        
        Args:
            codegen_token: Codegen API token
            
        Returns:
            bool: True if initialization was successful, False otherwise
        """
        try:
            # Initialize the Codegen agent if not already provided
            if not self.codegen_agent:
                self.codegen_agent = CodegenAgent(
                    app=self.app,
                    config=self.config,
                    logger=self.logger,
                    memory=self.memory
                )
            
            # Initialize the Codegen agent
            success = self.codegen_agent.initialize(codegen_token)
            self.is_initialized = success
            return success
        except Exception as e:
            logger.error(f"Failed to initialize Codegen agent: {str(e)}", exc_info=True)
            return False
    
    def set_project_context(
        self,
        project_name: str,
        project_description: str,
        requirements_text: str
    ) -> None:
        """
        Set the project context for the Codegen agent
        
        Args:
            project_name: Name of the project
            project_description: Description of the project
            requirements_text: Requirements text
        """
        if not self.is_initialized:
            raise ValueError("Codegen agent not initialized. Call initialize() first.")
            
        # Add input validation
        valid, error_msg = validate_required_params(
            {
                "project_name": project_name,
                "project_description": project_description,
                "requirements_text": requirements_text
            },
            ["project_name", "project_description", "requirements_text"]
        )
        
        if not valid:
            raise ValueError(error_msg)
            
        self.codegen_agent.set_project_context(
            project_name=project_name,
            project_description=project_description,
            requirements_text=requirements_text
        )
        
        self.current_project = project_name
    
    def parse_deployment_steps(self, deployment_plan: str) -> List[AtomicTask]:
        """
        Parse deployment steps from a deployment plan
        
        Args:
            deployment_plan: Deployment plan text
            
        Returns:
            List[AtomicTask]: List of deployment steps
        """
        if not self.is_initialized:
            raise ValueError("Codegen agent not initialized. Call initialize() first.")
            
        # Parse the deployment plan into steps
        steps = []
        
        # Split the plan into steps
        import re
        step_pattern = r"Step\s+(\d+):\s+(.*?)(?=Step\s+\d+:|$)"
        matches = re.finditer(step_pattern, deployment_plan, re.DOTALL)
        
        for match in matches:
            step_number = match.group(1)
            step_content = match.group(2).strip()
            
            # Split the step content into title and description
            lines = step_content.split("\n", 1)
            step_title = f"Step {step_number}: {lines[0]}"
            step_description = lines[1].strip() if len(lines) > 1 else ""
            
            # Create an atomic task for the step
            step = AtomicTask(
                id=f"step-{step_number}",
                title=step_title,
                description=step_description,
                priority=int(step_number),
                dependencies=[f"step-{i}" for i in range(1, int(step_number))],
                phase=1,
                status="pending",
                tags=["deployment"],
                estimated_time=0,
                assignee=None,
                interface_definition=False,
            )
            
            steps.append(step)
        
        # Store the deployment steps
        self.deployment_steps = steps
        
        return steps
    
    def execute_deployment_steps(self, max_concurrent_steps: int = 1) -> Dict[str, Any]:
        """
        Execute deployment steps
        
        Args:
            max_concurrent_steps: Maximum number of concurrent steps
            
        Returns:
            Dict[str, Any]: Results of the deployment steps
        """
        if not self.is_initialized:
            raise ValueError("Codegen agent not initialized. Call initialize() first.")
            
        if not self.deployment_steps:
            raise ValueError("No deployment steps to execute. Call parse_deployment_steps() first.")
            
        # Execute steps
        results = self.codegen_agent.execute_tasks(max_concurrent_tasks=max_concurrent_steps)
        
        # Store results with memory management
        self._manage_results_storage(results)
        
        return results
        
    async def execute_deployment_steps_async(self, max_concurrent_steps: int = 1) -> Dict[str, Any]:
        """
        Execute deployment steps asynchronously
        
        Args:
            max_concurrent_steps: Maximum number of concurrent steps
            
        Returns:
            Dict[str, Any]: Results of the deployment steps
        """
        if not self.is_initialized:
            raise ValueError("Codegen agent not initialized. Call initialize() first.")
            
        if not self.deployment_steps:
            raise ValueError("No deployment steps to execute. Call parse_deployment_steps() first.")
            
        # Execute steps asynchronously
        results = await self.codegen_agent.execute_tasks_async(max_concurrent_tasks=max_concurrent_steps)
        
        # Store results with memory management
        self._manage_results_storage(results)
        
        return results
        
    def _manage_results_storage(self, new_results: Dict[str, Any]) -> None:
        """
        Manage the storage of results to prevent memory leaks
        
        Args:
            new_results: New results to store
        """
        # Add new results to storage
        self.step_results.update(new_results)
        
        # If we have too many results, remove the oldest ones
        if len(self.step_results) > self.max_stored_results:
            # Sort keys by timestamp if available, otherwise just take the first ones
            keys_to_remove = sorted(
                self.step_results.keys(),
                key=lambda k: self.step_results[k].get("timestamp", 0) if isinstance(self.step_results[k], dict) else 0
            )[:len(self.step_results) - self.max_stored_results]
            
            # Remove oldest results
            for key in keys_to_remove:
                del self.step_results[key]
        
    def execute_single_step(self, step_id: str, step_title: str, step_description: str) -> TaskResult:
        """
        Execute a single deployment step
        
        Args:
            step_id: ID of the step
            step_title: Title of the step
            step_description: Description of the step
            
        Returns:
            TaskResult: Result of the step execution
        """
        if not self.is_initialized:
            raise ValueError("Codegen agent not initialized. Call initialize() first.")
            
        # Input validation
        valid, error_msg = validate_required_params(
            {
                "step_id": step_id,
                "step_title": step_title,
                "step_description": step_description
            },
            ["step_id", "step_title", "step_description"]
        )
        
        if not valid:
            raise ValueError(error_msg)
            
        # Create a step
        step = AtomicTask(
            id=step_id,
            title=step_title,
            description=step_description,
            priority=1,
            dependencies=[],
            phase=1,
            status="pending",
            tags=["deployment"],
            estimated_time=0,
            assignee=None,
            interface_definition=False,
        )
            
        # Execute step
        result = self.codegen_agent.execute_single_task(step)
        
        # Store result with memory management
        self.step_results[step_id] = result
        self._manage_results_storage({step_id: result})
        
        return result
        
    def get_step_status(self, step_id: str) -> Dict[str, Any]:
        """
        Get the status of a deployment step
        
        Args:
            step_id: ID of the step
            
        Returns:
            Dict[str, Any]: Status of the step
        """
        if not self.is_initialized:
            raise ValueError("Codegen agent not initialized. Call initialize() first.")
            
        return self.codegen_agent.get_task_status(step_id)
        
    def get_step_result(self, step_id: str) -> Dict[str, Any]:
        """
        Get the result of a deployment step
        
        Args:
            step_id: ID of the step
            
        Returns:
            Dict[str, Any]: Result of the step
        """
        if not self.is_initialized:
            raise ValueError("Codegen agent not initialized. Call initialize() first.")
            
        return self.codegen_agent.get_task_result(step_id)
        
    def get_all_step_results(self) -> Dict[str, Any]:
        """
        Get all deployment step results
        
        Returns:
            Dict[str, Any]: All step results
        """
        if not self.is_initialized:
            raise ValueError("Codegen agent not initialized. Call initialize() first.")
            
        with self.step_results:
            return self.step_results.copy()
        
    def get_status(self) -> Dict[str, Any]:
        """
        Get the status of the weaver integration
        
        Returns:
            Dict[str, Any]: Status of the weaver integration
        """
        status = {
            "initialized": self.is_initialized,
            "current_project": self.current_project,
            "deployment_steps": len(self.deployment_steps),
        }
        
        if self.is_initialized and self.codegen_agent:
            status.update(self.codegen_agent.get_status())
            
        return status
        
    def cancel_all_steps(self) -> bool:
        """
        Cancel all running deployment steps
        
        Returns:
            bool: True if cancellation was successful, False otherwise
        """
        return self.codegen_agent.cancel_all_tasks()
