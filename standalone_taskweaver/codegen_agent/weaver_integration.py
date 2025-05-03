#!/usr/bin/env python3
"""
WeaverCodegenIntegration - Bridge between TaskWeaver and Codegen Agent

This module provides a comprehensive integration between TaskWeaver's planner
and the Codegen agent, allowing TaskWeaver to delegate deployment tasks to
Codegen and monitor their progress.
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
from standalone_taskweaver.planner.planner import Planner
from standalone_taskweaver.codegen_agent.integration import CodegenIntegration
from standalone_taskweaver.codegen_agent.codegen_agent import CodegenAgent, CodegenAgentStatus
from standalone_taskweaver.codegen_agent.requirements_manager import RequirementsManager, AtomicTask, DependencyGraph
from standalone_taskweaver.codegen_agent.concurrent_execution import ConcurrentExecutionEngine, TaskStatus, TaskResult

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("weaver-codegen-integration")

class DeploymentTaskStatus:
    """
    Status of a deployment task
    """
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"

class DeploymentTask:
    """
    Deployment task representation
    """
    def __init__(
        self,
        task_id: str,
        description: str,
        context: Dict[str, Any] = None,
        atomic_tasks: List[AtomicTask] = None,
        status: str = DeploymentTaskStatus.PENDING,
        results: Dict[str, Any] = None,
    ):
        self.task_id = task_id
        self.description = description
        self.context = context or {}
        self.atomic_tasks = atomic_tasks or []
        self.status = status
        self.results = results or {}
        self.created_at = None
        self.updated_at = None
        self.completed_at = None

class WeaverCodegenIntegration:
    """
    Integration class between TaskWeaver and Codegen Agent
    
    This class provides a bridge between TaskWeaver's planner and the Codegen agent,
    allowing TaskWeaver to delegate deployment tasks to Codegen and monitor their progress.
    """
    
    @inject
    def __init__(
        self,
        app: TaskWeaverApp,
        config: AppConfigSource,
        logger: TelemetryLogger,
        codegen_integration: CodegenIntegration,
        codegen_agent: Optional[CodegenAgent] = None,
        memory: Optional[Memory] = None,
    ) -> None:
        self.app = app
        self.config = config
        self.logger = logger
        self.codegen_integration = codegen_integration
        self.codegen_agent = codegen_agent
        self.memory = memory or Memory()
        
        # Task tracking
        self.deployment_tasks = {}
        self.current_task_id = None
        
        # Initialize components if needed
        if not self.codegen_agent and self.codegen_integration.is_initialized:
            self.codegen_agent = CodegenAgent(
                app=app,
                config=config,
                logger=logger,
                memory=self.memory
            )
    
    def is_deployment_task(self, task_description: str) -> bool:
        """
        Determine if a task is deployment-related
        
        Args:
            task_description: Task description
            
        Returns:
            bool: True if the task is deployment-related, False otherwise
        """
        # Check for deployment-related keywords
        deployment_keywords = [
            "deploy", "deployment", "release", "publish", "provision", 
            "infrastructure", "cloud", "server", "container", "docker", 
            "kubernetes", "k8s", "aws", "azure", "gcp", "terraform", 
            "ansible", "chef", "puppet", "ci/cd", "pipeline", "continuous integration",
            "continuous deployment", "continuous delivery", "environment"
        ]
        
        # Check if any of the keywords are in the task description
        for keyword in deployment_keywords:
            if keyword.lower() in task_description.lower():
                return True
                
        return False
    
    def create_deployment_task(
        self, 
        task_description: str, 
        context: Dict[str, Any] = None
    ) -> str:
        """
        Create a deployment task
        
        Args:
            task_description: Task description
            context: Optional context for the task
            
        Returns:
            str: Task ID
        """
        import uuid
        import datetime
        
        task_id = f"deploy-{uuid.uuid4().hex[:8]}"
        
        task = DeploymentTask(
            task_id=task_id,
            description=task_description,
            context=context or {},
            status=DeploymentTaskStatus.PENDING
        )
        
        task.created_at = datetime.datetime.now().isoformat()
        task.updated_at = task.created_at
        
        self.deployment_tasks[task_id] = task
        
        return task_id
    
    def get_deployment_task(self, task_id: str) -> Optional[DeploymentTask]:
        """
        Get a deployment task by ID
        
        Args:
            task_id: Task ID
            
        Returns:
            Optional[DeploymentTask]: Deployment task if found, None otherwise
        """
        return self.deployment_tasks.get(task_id)
    
    def update_deployment_task_status(self, task_id: str, status: str) -> bool:
        """
        Update the status of a deployment task
        
        Args:
            task_id: Task ID
            status: New status
            
        Returns:
            bool: True if the task was updated, False otherwise
        """
        import datetime
        
        task = self.get_deployment_task(task_id)
        
        if not task:
            return False
        
        task.status = status
        task.updated_at = datetime.datetime.now().isoformat()
        
        if status == DeploymentTaskStatus.COMPLETED or status == DeploymentTaskStatus.FAILED:
            task.completed_at = task.updated_at
        
        return True
    
    def _create_atomic_tasks(self, task_description: str, context: Dict[str, Any]) -> List[AtomicTask]:
        """
        Create atomic tasks from a deployment task description
        
        Args:
            task_description: Task description
            context: Context for the task
            
        Returns:
            List[AtomicTask]: List of atomic tasks
        """
        # Create a prompt for the task breakdown
        prompt = f"""
        # Deployment Task: {task_description}
        
        ## Context
        {json.dumps(context, indent=2)}
        
        ## Instructions
        Break down this deployment task into atomic steps that can be executed independently.
        Each step should be a small, focused task that can be completed in a reasonable amount of time.
        """
        
        # Use Codegen to break down the task
        if not self.codegen_integration.is_initialized:
            raise ValueError("Codegen integration not initialized")
        
        # Execute the task using Codegen
        result = self.codegen_integration.run_codegen_task(prompt)
        
        # Parse the result to extract atomic tasks
        atomic_tasks = []
        
        try:
            # Assume the result contains a list of tasks
            tasks_data = json.loads(result.get("result", "[]"))
            
            for i, task_data in enumerate(tasks_data):
                atomic_task = AtomicTask(
                    id=f"atomic-{i+1}",
                    title=task_data.get("title", f"Step {i+1}"),
                    description=task_data.get("description", ""),
                    priority=i,
                    dependencies=task_data.get("dependencies", []),
                    phase=1,
                    status="pending",
                    tags=["deployment"],
                    estimated_time=0,
                    assignee=None,
                    interface_definition=False,
                )
                
                atomic_tasks.append(atomic_task)
        except Exception as e:
            logger.error(f"Error parsing atomic tasks: {str(e)}")
            
            # Fallback: create a single atomic task
            atomic_task = AtomicTask(
                id="atomic-1",
                title=task_description,
                description=task_description,
                priority=0,
                dependencies=[],
                phase=1,
                status="pending",
                tags=["deployment"],
                estimated_time=0,
                assignee=None,
                interface_definition=False,
            )
            
            atomic_tasks = [atomic_task]
        
        return atomic_tasks
    
    def delegate_to_codegen(self, task_id: str) -> bool:
        """
        Delegate a deployment task to Codegen
        
        Args:
            task_id: Task ID
            
        Returns:
            bool: True if the task was delegated successfully, False otherwise
        """
        import datetime
        
        task = self.get_deployment_task(task_id)
        
        if not task:
            return False
        
        if not self.codegen_integration.is_initialized:
            logger.error("Codegen integration not initialized")
            self.update_deployment_task_status(task_id, DeploymentTaskStatus.FAILED)
            return False
        
        # Update task status
        self.update_deployment_task_status(task_id, DeploymentTaskStatus.RUNNING)
        
        # Create atomic tasks
        try:
            atomic_tasks = self._create_atomic_tasks(task.description, task.context)
            task.atomic_tasks = atomic_tasks
            
            # Execute the tasks using Codegen
            self.current_task_id = task_id
            
            # Start execution in a separate thread
            import threading
            
            def execute_tasks():
                try:
                    # Execute tasks
                    results = asyncio.run(self.codegen_integration.execute_tasks(atomic_tasks))
                    
                    # Update task with results
                    task.results = {
                        "atomic_tasks": [result.to_dict() for result in results],
                        "summary": self._generate_summary(results)
                    }
                    
                    # Update task status
                    if all(result.status.value == "completed" for result in results):
                        self.update_deployment_task_status(task_id, DeploymentTaskStatus.COMPLETED)
                    else:
                        self.update_deployment_task_status(task_id, DeploymentTaskStatus.FAILED)
                except Exception as e:
                    logger.error(f"Error executing tasks: {str(e)}")
                    self.update_deployment_task_status(task_id, DeploymentTaskStatus.FAILED)
                    task.results = {
                        "error": str(e)
                    }
                finally:
                    self.current_task_id = None
            
            # Start execution thread
            thread = threading.Thread(target=execute_tasks)
            thread.daemon = True
            thread.start()
            
            return True
        except Exception as e:
            logger.error(f"Error delegating task to Codegen: {str(e)}")
            self.update_deployment_task_status(task_id, DeploymentTaskStatus.FAILED)
            task.results = {
                "error": str(e)
            }
            return False
    
    def _generate_summary(self, results: List[TaskResult]) -> Dict[str, Any]:
        """
        Generate a summary of task results
        
        Args:
            results: List of task results
            
        Returns:
            Dict[str, Any]: Summary of results
        """
        total_tasks = len(results)
        completed_tasks = sum(1 for result in results if result.status.value == "completed")
        failed_tasks = sum(1 for result in results if result.status.value == "failed")
        
        return {
            "total_tasks": total_tasks,
            "completed_tasks": completed_tasks,
            "failed_tasks": failed_tasks,
            "success_rate": completed_tasks / total_tasks if total_tasks > 0 else 0
        }
    
    def get_deployment_task_status(self, task_id: str) -> Dict[str, Any]:
        """
        Get the status of a deployment task
        
        Args:
            task_id: Task ID
            
        Returns:
            Dict[str, Any]: Task status
        """
        task = self.get_deployment_task(task_id)
        
        if not task:
            return {
                "task_id": task_id,
                "status": "not_found"
            }
        
        return {
            "task_id": task.task_id,
            "description": task.description,
            "status": task.status,
            "created_at": task.created_at,
            "updated_at": task.updated_at,
            "completed_at": task.completed_at,
            "atomic_tasks": [
                {
                    "id": atomic_task.id,
                    "title": atomic_task.title,
                    "status": atomic_task.status
                }
                for atomic_task in task.atomic_tasks
            ]
        }
    
    def get_deployment_task_results(self, task_id: str) -> Dict[str, Any]:
        """
        Get the results of a deployment task
        
        Args:
            task_id: Task ID
            
        Returns:
            Dict[str, Any]: Task results
        """
        task = self.get_deployment_task(task_id)
        
        if not task:
            return {
                "task_id": task_id,
                "status": "not_found"
            }
        
        return {
            "task_id": task.task_id,
            "description": task.description,
            "status": task.status,
            "results": task.results
        }
    
    def generate_deployment_report(self, task_id: str) -> Dict[str, Any]:
        """
        Generate a report for a deployment task
        
        Args:
            task_id: Task ID
            
        Returns:
            Dict[str, Any]: Deployment report
        """
        task = self.get_deployment_task(task_id)
        
        if not task:
            return {
                "task_id": task_id,
                "status": "not_found"
            }
        
        # Generate a report using Codegen
        if not self.codegen_integration.is_initialized:
            return {
                "task_id": task_id,
                "error": "Codegen integration not initialized"
            }
        
        # Create a prompt for the report
        prompt = f"""
        # Deployment Report for: {task.description}
        
        ## Task Details
        - Task ID: {task.task_id}
        - Status: {task.status}
        - Created: {task.created_at}
        - Completed: {task.completed_at or "N/A"}
        
        ## Results
        {json.dumps(task.results, indent=2)}
        
        ## Instructions
        Generate a comprehensive deployment report based on the information above.
        Include a summary, details of each step, any issues encountered, and recommendations for future deployments.
        """
        
        # Execute the task using Codegen
        result = self.codegen_integration.run_codegen_task(prompt)
        
        # Return the report
        return {
            "task_id": task.task_id,
            "description": task.description,
            "status": task.status,
            "report": result.get("result", "Failed to generate report")
        }
    
    def add_to_memory(self, task_id: str, planner: Planner) -> bool:
        """
        Add deployment task results to TaskWeaver's memory
        
        Args:
            task_id: Task ID
            planner: TaskWeaver planner
            
        Returns:
            bool: True if the results were added successfully, False otherwise
        """
        task = self.get_deployment_task(task_id)
        
        if not task:
            return False
        
        # Add the results to the memory
        try:
            # Create a task in the planner if it doesn't exist
            if not planner.get_task(task_id):
                planner.create_task(
                    task_id=task_id,
                    description=task.description,
                    status="pending"
                )
            
            # Update the task with the result
            planner_task = planner.get_task(task_id)
            planner_task.result = task.results
            
            # Mark the task as completed if successful
            if task.status == DeploymentTaskStatus.COMPLETED:
                planner_task.status = "completed"
            else:
                planner_task.status = "failed"
            
            # Update the task in the planner
            planner.update_task(planner_task)
            
            return True
        except Exception as e:
            logger.error(f"Error adding results to memory: {str(e)}")
            return False
    
    def cancel_deployment_task(self, task_id: str) -> bool:
        """
        Cancel a deployment task
        
        Args:
            task_id: Task ID
            
        Returns:
            bool: True if the task was cancelled successfully, False otherwise
        """
        task = self.get_deployment_task(task_id)
        
        if not task:
            return False
        
        # Only cancel if the task is pending or running
        if task.status not in [DeploymentTaskStatus.PENDING, DeploymentTaskStatus.RUNNING]:
            return False
        
        # Cancel the task
        self.update_deployment_task_status(task_id, DeploymentTaskStatus.CANCELLED)
        
        # Cancel atomic tasks if they are running
        if self.current_task_id == task_id and self.codegen_integration.is_initialized:
            self.codegen_integration.cancel_tasks([atomic_task.id for atomic_task in task.atomic_tasks])
        
        return True
    
    def list_deployment_tasks(self) -> List[Dict[str, Any]]:
        """
        List all deployment tasks
        
        Returns:
            List[Dict[str, Any]]: List of deployment tasks
        """
        return [
            {
                "task_id": task.task_id,
                "description": task.description,
                "status": task.status,
                "created_at": task.created_at,
                "updated_at": task.updated_at,
                "completed_at": task.completed_at
            }
            for task in self.deployment_tasks.values()
        ]

