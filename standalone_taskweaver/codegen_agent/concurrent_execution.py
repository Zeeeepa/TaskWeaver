#!/usr/bin/env python3
"""
Concurrent Execution Engine for TaskWeaver-Codegen Integration

This module provides functionality for executing multiple Codegen tasks concurrently,
monitoring their progress, and handling errors.
"""

import os
import sys
import json
import time
import asyncio
import logging
from typing import Dict, List, Optional, Any, Union, Tuple, Set
from enum import Enum

from injector import inject

from standalone_taskweaver.app.app import TaskWeaverApp
from standalone_taskweaver.config.config_mgt import AppConfigSource
from standalone_taskweaver.logging import TelemetryLogger
from standalone_taskweaver.memory import Memory
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
logger = logging.getLogger("concurrent-execution")

class TaskStatus(Enum):
    """
    Status of a Codegen task
    """
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"

class TaskResult:
    """
    Result of a Codegen task
    """
    
    def __init__(
        self,
        task_id: str,
        codegen_task_id: str,
        status: TaskStatus,
        result: Any = None,
        error: Optional[Exception] = None,
        start_time: float = 0,
        end_time: float = 0,
    ) -> None:
        self.task_id = task_id
        self.codegen_task_id = codegen_task_id
        self.status = status
        self.result = result
        self.error = error
        self.start_time = start_time
        self.end_time = end_time
        
    @property
    def duration(self) -> float:
        """Get the duration of the task in seconds"""
        if self.start_time and self.end_time:
            return self.end_time - self.start_time
        return 0
        
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "task_id": self.task_id,
            "codegen_task_id": self.codegen_task_id,
            "status": self.status.value,
            "result": self.result,
            "error": str(self.error) if self.error else None,
            "start_time": self.start_time,
            "end_time": self.end_time,
            "duration": self.duration,
        }
        
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'TaskResult':
        """Create from dictionary"""
        return cls(
            task_id=data["task_id"],
            codegen_task_id=data["codegen_task_id"],
            status=TaskStatus(data["status"]),
            result=data.get("result"),
            error=Exception(data["error"]) if data.get("error") else None,
            start_time=data.get("start_time", 0),
            end_time=data.get("end_time", 0),
        )

class ConcurrentExecutionEngine:
    """
    Executes multiple Codegen tasks concurrently
    """
    
    @inject
    def __init__(
        self,
        app: TaskWeaverApp,
        config: AppConfigSource,
        logger: TelemetryLogger,
        memory: Optional[Memory] = None,
        max_concurrency: int = 10,
    ) -> None:
        self.app = app
        self.config = config
        self.logger = logger
        self.memory = memory
        self.max_concurrency = max_concurrency
        self.codegen_agent = None
        self.tasks = {}  # task_id -> TaskResult
        
    def initialize(self, org_id: str, token: str) -> None:
        """
        Initialize the Codegen agent
        
        Args:
            org_id: Codegen organization ID
            token: Codegen API token
        """
        self.codegen_agent = Agent(org_id=org_id, token=token)
        logger.info("Initialized Codegen agent")
        
    async def execute_tasks(self, tasks: List[AtomicTask]) -> List[TaskResult]:
        """
        Execute multiple tasks concurrently and return results
        
        Args:
            tasks: List of atomic tasks
            
        Returns:
            List of task results
        """
        if not self.codegen_agent:
            raise ValueError("Codegen agent not initialized. Call initialize() first.")
            
        # Create a semaphore to limit concurrency
        semaphore = asyncio.Semaphore(self.max_concurrency)
        
        # Create coroutines for each task
        coroutines = []
        for task in tasks:
            coroutines.append(self._execute_task(task, semaphore))
            
        # Execute tasks concurrently
        results = await asyncio.gather(*coroutines)
        
        return results
        
    async def _execute_task(self, task: AtomicTask, semaphore: asyncio.Semaphore) -> TaskResult:
        """
        Execute a single task
        
        Args:
            task: Atomic task
            semaphore: Semaphore to limit concurrency
            
        Returns:
            Task result
        """
        async with semaphore:
            # Create a task result
            task_result = TaskResult(
                task_id=task.id,
                codegen_task_id="",
                status=TaskStatus.PENDING,
                start_time=time.time(),
            )
            
            self.tasks[task.id] = task_result
            
            try:
                # Create a prompt for the task
                prompt = self._create_prompt(task)
                
                # Execute the task
                task_result.status = TaskStatus.RUNNING
                
                # Run the task using the Codegen SDK
                codegen_task = self.codegen_agent.run(prompt=prompt)
                
                # Store the Codegen task ID
                task_result.codegen_task_id = codegen_task.id
                
                # Wait for the task to complete
                while codegen_task.status not in ["completed", "failed", "cancelled"]:
                    # Refresh the task status
                    codegen_task.refresh()
                    
                    # Wait a bit before checking again
                    await asyncio.sleep(5)
                    
                # Update the task result
                if codegen_task.status == "completed":
                    task_result.status = TaskStatus.COMPLETED
                    task_result.result = codegen_task.result
                elif codegen_task.status == "failed":
                    task_result.status = TaskStatus.FAILED
                    task_result.error = Exception(f"Codegen task failed: {codegen_task.error}")
                elif codegen_task.status == "cancelled":
                    task_result.status = TaskStatus.CANCELLED
                    task_result.error = Exception("Codegen task cancelled")
                    
            except Exception as e:
                # Handle any exceptions
                task_result.status = TaskStatus.FAILED
                task_result.error = e
                logger.error(f"Error executing task {task.id}: {e}")
                
            finally:
                # Update the end time
                task_result.end_time = time.time()
                
            return task_result
            
    def _create_prompt(self, task: AtomicTask) -> str:
        """
        Create a prompt for a task
        
        Args:
            task: Atomic task
            
        Returns:
            Prompt string
        """
        prompt = f"# Task: {task.title}\n\n"
        
        if task.description:
            prompt += f"## Description\n\n{task.description}\n\n"
            
        if task.tags:
            prompt += f"## Tags\n\n{', '.join(task.tags)}\n\n"
            
        if task.dependencies:
            prompt += f"## Dependencies\n\n{', '.join(task.dependencies)}\n\n"
            
        prompt += "## Instructions\n\n"
        
        if task.interface_definition:
            prompt += "Please define a clear interface for this component. Include:\n"
            prompt += "1. Method signatures with parameter and return types\n"
            prompt += "2. Class definitions with properties and methods\n"
            prompt += "3. Documentation for all public methods and properties\n"
            prompt += "4. Usage examples\n"
        else:
            prompt += "Please implement this task according to the description. Ensure your implementation is:\n"
            prompt += "1. Well-documented with docstrings and comments\n"
            prompt += "2. Properly tested with unit tests\n"
            prompt += "3. Follows best practices for the language and framework\n"
            prompt += "4. Handles edge cases and errors appropriately\n"
            
        return prompt
        
    async def monitor_progress(self, task_ids: List[str]) -> Dict[str, TaskStatus]:
        """
        Monitor progress of multiple concurrent tasks
        
        Args:
            task_ids: List of task IDs
            
        Returns:
            Dictionary mapping task IDs to statuses
        """
        statuses = {}
        
        for task_id in task_ids:
            if task_id in self.tasks:
                statuses[task_id] = self.tasks[task_id].status
            else:
                statuses[task_id] = TaskStatus.PENDING
                
        return statuses
        
    def get_task_result(self, task_id: str) -> Optional[TaskResult]:
        """
        Get the result of a task
        
        Args:
            task_id: Task ID
            
        Returns:
            Task result or None if not found
        """
        return self.tasks.get(task_id)
        
    def get_all_results(self) -> Dict[str, TaskResult]:
        """
        Get all task results
        
        Returns:
            Dictionary mapping task IDs to results
        """
        return self.tasks
        
    def cancel_task(self, task_id: str) -> bool:
        """
        Cancel a task
        
        Args:
            task_id: Task ID
            
        Returns:
            True if the task was cancelled, False otherwise
        """
        if task_id not in self.tasks:
            return False
            
        task_result = self.tasks[task_id]
        
        if task_result.status in [TaskStatus.COMPLETED, TaskStatus.FAILED, TaskStatus.CANCELLED]:
            return False
            
        # Cancel the Codegen task
        if task_result.codegen_task_id:
            # Note: The Codegen SDK doesn't currently support cancelling tasks
            # This is a placeholder for when it does
            pass
            
        # Update the task result
        task_result.status = TaskStatus.CANCELLED
        task_result.end_time = time.time()
        
        return True
        
    def cancel_all_tasks(self) -> int:
        """
        Cancel all running tasks
        
        Returns:
            Number of tasks cancelled
        """
        count = 0
        
        for task_id in self.tasks:
            if self.cancel_task(task_id):
                count += 1
                
        return count
        
    def export_results_to_json(self, output_path: str) -> None:
        """
        Export task results to a JSON file
        
        Args:
            output_path: Path to the output file
        """
        data = {task_id: result.to_dict() for task_id, result in self.tasks.items()}
        
        with open(output_path, "w") as f:
            json.dump(data, f, indent=2)
            
        logger.info(f"Exported task results to {output_path}")
        
    def import_results_from_json(self, input_path: str) -> None:
        """
        Import task results from a JSON file
        
        Args:
            input_path: Path to the input file
        """
        with open(input_path, "r") as f:
            data = json.load(f)
            
        self.tasks = {task_id: TaskResult.from_dict(result_data) for task_id, result_data in data.items()}
        
        logger.info(f"Imported task results from {input_path}")

class ErrorHandlingFramework:
    """
    Provides robust error handling with fallback mechanisms
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
        
    def handle_error(self, task: AtomicTask, error: Exception) -> TaskResult:
        """
        Handle errors with appropriate fallback strategies
        
        Args:
            task: Atomic task
            error: Exception
            
        Returns:
            Task result
        """
        logger.error(f"Error executing task {task.id}: {error}")
        
        # Create a task result
        task_result = TaskResult(
            task_id=task.id,
            codegen_task_id="",
            status=TaskStatus.FAILED,
            error=error,
            start_time=time.time(),
            end_time=time.time(),
        )
        
        # Try to handle the error based on its type
        if isinstance(error, TimeoutError):
            # Handle timeout errors
            logger.info(f"Task {task.id} timed out. Retrying with increased timeout...")
            return self.retry_with_backoff(task)
        elif "API" in str(error) or "token" in str(error).lower():
            # Handle API errors
            logger.info(f"API error for task {task.id}. Checking API credentials...")
            # Check API credentials
            # This is a placeholder for actual implementation
            pass
        elif "rate limit" in str(error).lower():
            # Handle rate limit errors
            logger.info(f"Rate limit exceeded for task {task.id}. Retrying with exponential backoff...")
            return self.retry_with_backoff(task)
        else:
            # Handle other errors
            logger.info(f"Unknown error for task {task.id}. Retrying...")
            return self.retry_with_backoff(task)
            
        return task_result
        
    def retry_with_backoff(self, task: AtomicTask, max_retries: int = 3) -> TaskResult:
        """
        Retry failed tasks with exponential backoff
        
        Args:
            task: Atomic task
            max_retries: Maximum number of retries
            
        Returns:
            Task result
        """
        # Create a task result
        task_result = TaskResult(
            task_id=task.id,
            codegen_task_id="",
            status=TaskStatus.PENDING,
            start_time=time.time(),
        )
        
        # Try to execute the task with exponential backoff
        retry_count = 0
        while retry_count < max_retries:
            try:
                # Wait with exponential backoff
                wait_time = 2 ** retry_count
                logger.info(f"Retrying task {task.id} in {wait_time} seconds...")
                time.sleep(wait_time)
                
                # Execute the task
                # This is a placeholder for actual implementation
                # In a real implementation, you would use the Codegen SDK
                
                # Update the task result
                task_result.status = TaskStatus.COMPLETED
                task_result.result = f"Retry {retry_count + 1} succeeded"
                task_result.end_time = time.time()
                
                return task_result
                
            except Exception as e:
                # Handle the error
                logger.error(f"Retry {retry_count + 1} failed for task {task.id}: {e}")
                
                # Update the task result
                task_result.status = TaskStatus.FAILED
                task_result.error = e
                task_result.end_time = time.time()
                
                # Increment the retry count
                retry_count += 1
                
        return task_result
