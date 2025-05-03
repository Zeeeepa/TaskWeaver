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
from standalone_taskweaver.codegen_agent.requirements_manager import AtomicTask, DependencyGraph
from standalone_taskweaver.codegen_agent.concurrent_execution import TaskResult

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
            task_description: Task description
            
        Returns:
            bool: True if the task is code-related, False otherwise
        """
        # Check for code-related keywords
        code_keywords = [
            "code", "implement", "function", "class", "method", "api",
            "endpoint", "interface", "module", "library", "package",
            "script", "program", "algorithm", "data structure", "refactor",
            "optimize", "debug", "fix", "test", "unit test", "integration test",
            "documentation", "comment", "docstring", "type hint", "annotation"
        ]
        
        # Check if any of the keywords are in the task description
        for keyword in code_keywords:
            if keyword in task_description.lower():
                return True
                
        return False
        
    def delegate_to_codegen(self, task_description: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Delegate a task to Codegen
        
        Args:
            task_description: Task description
            context: Optional context for the task
            
        Returns:
            Dict[str, Any]: Result of the task
        """
        if not self.codegen_integration.is_initialized:
            raise ValueError("Codegen integration not initialized")
            
        # Create a prompt for the task
        prompt = self._create_prompt(task_description, context)
        
        # Execute the task using Codegen
        task = self.codegen_integration.run_codegen_task(prompt)
        
        # Wait for the task to complete
        while self.codegen_integration.get_task_status(task) not in ["completed", "failed", "cancelled"]:
            # Wait a bit before checking again
            import time
            time.sleep(5)
            
        # Get the result
        result = self.codegen_integration.get_task_result(task)
        
        # Return the result
        return {
            "task_description": task_description,
            "result": result,
            "status": self.codegen_integration.get_task_status(task),
        }
        
    def _create_prompt(self, task_description: str, context: Dict[str, Any] = None) -> str:
        """
        Create a prompt for a task
        
        Args:
            task_description: Task description
            context: Optional context for the task
            
        Returns:
            str: Prompt for the task
        """
        prompt = f"# Task: {task_description}\n\n"
        
        if context:
            prompt += "## Context\n\n"
            
            # Add context information
            for key, value in context.items():
                prompt += f"### {key}\n\n"
                
                if isinstance(value, dict):
                    for k, v in value.items():
                        prompt += f"- {k}: {v}\n"
                elif isinstance(value, list):
                    for item in value:
                        prompt += f"- {item}\n"
                else:
                    prompt += f"{value}\n"
                    
                prompt += "\n"
                
        prompt += "## Instructions\n\n"
        prompt += "Please implement this task according to the description and context provided.\n"
        prompt += "Ensure your implementation is well-documented, properly tested, and follows best practices.\n"
        
        return prompt
        
    def incorporate_codegen_result(self, planner: Planner, task_id: str, result: Dict[str, Any]) -> None:
        """
        Incorporate Codegen result into the planner
        
        Args:
            planner: TaskWeaver planner
            task_id: Task ID
            result: Result from Codegen
        """
        # Get the task from the planner
        task = planner.get_task(task_id)
        
        if not task:
            logger.warning(f"Task {task_id} not found in planner")
            return
            
        # Update the task with the result
        task.result = result.get("result", "")
        
        # Mark the task as completed if successful
        if result.get("status") == "completed":
            task.status = "completed"
        else:
            task.status = "failed"
            
        # Update the task in the planner
        planner.update_task(task)
        
    def delegate_atomic_tasks(self, tasks: List[AtomicTask]) -> List[TaskResult]:
        """
        Delegate a list of atomic tasks to Codegen for concurrent execution
        
        Args:
            tasks: List of atomic tasks
            
        Returns:
            List[TaskResult]: Results of the tasks
        """
        if not self.codegen_integration.is_initialized:
            raise ValueError("Codegen integration not initialized")
            
        # Execute the tasks concurrently
        import asyncio
        results = asyncio.run(self.codegen_integration.execute_tasks(tasks))
        
        return results
        
    def incorporate_atomic_task_results(self, planner: Planner, results: List[TaskResult]) -> None:
        """
        Incorporate results of atomic tasks into the planner
        
        Args:
            planner: TaskWeaver planner
            results: Results of atomic tasks
        """
        for result in results:
            # Create a task in the planner if it doesn't exist
            if not planner.get_task(result.task_id):
                planner.create_task(
                    task_id=result.task_id,
                    description=f"Codegen task {result.task_id}",
                    status="pending"
                )
                
            # Update the task with the result
            task = planner.get_task(result.task_id)
            task.result = result.result
            
            # Mark the task as completed if successful
            if result.status.value == "completed":
                task.status = "completed"
            else:
                task.status = "failed"
                
            # Update the task in the planner
            planner.update_task(task)
            
    def create_atomic_tasks_from_plan(self, planner: Planner) -> List[AtomicTask]:
        """
        Create atomic tasks from a planner's tasks
        
        Args:
            planner: TaskWeaver planner
            
        Returns:
            List[AtomicTask]: List of atomic tasks
        """
        atomic_tasks = []
        
        for task_id, task in planner.tasks.items():
            # Only include code-related tasks
            if self.is_code_related_task(task.description):
                atomic_task = AtomicTask(
                    id=task_id,
                    title=task.description,
                    description=task.description,
                    priority=0,
                    dependencies=[],
                    phase=1,
                    status="pending",
                    tags=["planner"],
                    estimated_time=0,
                    assignee=None,
                    interface_definition=False,
                )
                
                atomic_tasks.append(atomic_task)
                
        return atomic_tasks
        
    def identify_dependencies_from_plan(self, planner: Planner, tasks: List[AtomicTask]) -> DependencyGraph:
        """
        Identify dependencies between tasks based on the planner's task dependencies
        
        Args:
            planner: TaskWeaver planner
            tasks: List of atomic tasks
            
        Returns:
            DependencyGraph: Dependency graph
        """
        # Create a mapping from task ID to atomic task
        task_map = {task.id: task for task in tasks}
        
        # Update dependencies based on planner's task dependencies
        for task_id, task in planner.tasks.items():
            if task_id in task_map:
                atomic_task = task_map[task_id]
                
                # Add dependencies
                for dep_id in task.dependencies:
                    if dep_id in task_map:
                        atomic_task.dependencies.append(dep_id)
                        
        # Create a dependency graph
        graph = self.codegen_integration.identify_dependencies(tasks)
        
        return graph
        
    def execute_plan_with_codegen(self, planner: Planner) -> Dict[str, Any]:
        """
        Execute a plan using Codegen for code-related tasks
        
        Args:
            planner: TaskWeaver planner
            
        Returns:
            Dict[str, Any]: Results of the execution
        """
        # Create atomic tasks from the plan
        tasks = self.create_atomic_tasks_from_plan(planner)
        
        # Identify dependencies
        graph = self.identify_dependencies_from_plan(planner, tasks)
        
        # Prioritize tasks
        phases = self.codegen_integration.prioritize_tasks(graph)
        
        # Execute tasks in phases
        all_results = []
        
        for phase_index, phase in enumerate(phases):
            logger.info(f"Executing phase {phase_index + 1} with {len(phase)} tasks")
            
            # Execute tasks in this phase
            results = self.delegate_atomic_tasks(phase)
            
            # Incorporate results
            self.incorporate_atomic_task_results(planner, results)
            
            # Add results to all_results
            all_results.extend(results)
            
        return {
            "phases": len(phases),
            "tasks": len(tasks),
            "results": all_results,
        }
        
    def generate_interfaces_for_plan(self, planner: Planner) -> Dict[str, str]:
        """
        Generate interfaces for components in the plan
        
        Args:
            planner: TaskWeaver planner
            
        Returns:
            Dict[str, str]: Mapping from component name to interface definition
        """
        interfaces = {}
        
        # Find components in the plan
        for task_id, task in planner.tasks.items():
            # Check if the task is about a component
            if any(keyword in task.description.lower() for keyword in ["component", "service", "module", "api"]):
                # Extract component name
                import re
                component_match = re.search(r'\b([A-Z][a-z]+(?:[A-Z][a-z]+)*)\b', task.description)
                
                if component_match:
                    component_name = component_match.group(1)
                    
                    # Create component specification
                    component_spec = {
                        "name": component_name,
                        "description": task.description,
                        "task_id": task_id,
                    }
                    
                    # Generate interface
                    interface = self.codegen_integration.generate_interface(component_spec)
                    
                    # Store the interface
                    interfaces[component_name] = interface
                    
        return interfaces
        
    def create_mock_implementations(self, interfaces: Dict[str, str]) -> Dict[str, str]:
        """
        Create mock implementations for interfaces
        
        Args:
            interfaces: Mapping from component name to interface definition
            
        Returns:
            Dict[str, str]: Mapping from component name to mock implementation
        """
        mock_implementations = {}
        
        for component_name, interface in interfaces.items():
            # Create mock implementation
            mock = self.codegen_integration.create_mock_implementation(interface)
            
            # Store the mock implementation
            mock_implementations[component_name] = mock
            
        return mock_implementations
