#!/usr/bin/env python3
"""
Concurrent Execution Engine for Codegen Agent

This module provides a concurrent execution engine for the Codegen agent,
allowing for parallel execution of tasks.
"""

import os
import sys
import json
import time
import asyncio
import logging
import threading
from concurrent.futures import ThreadPoolExecutor
from typing import Dict, List, Optional, Any, Union, Tuple, Set
from enum import Enum

from injector import inject

from standalone_taskweaver.app.app import TaskWeaverApp
from standalone_taskweaver.config.config_mgt import AppConfigSource
from standalone_taskweaver.logging import TelemetryLogger
from standalone_taskweaver.memory import Memory
from standalone_taskweaver.codegen_agent.requirements_manager import AtomicTask
from standalone_taskweaver.codegen_agent.utils import safe_execute, validate_required_params

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("concurrent-execution")

class TaskStatus(Enum):
    """
    Status of a task
    """
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"

class TaskResult:
    """
    Result of a task execution
    """
    def __init__(
        self,
        id: str,
        status: TaskStatus,
        result: Optional[Any] = None,
        error: Optional[str] = None,
        start_time: Optional[float] = None,
        end_time: Optional[float] = None,
        duration: Optional[float] = None,
    ) -> None:
        self.id = id
        self.status = status
        self.result = result
        self.error = error
        self.start_time = start_time or time.time()
        self.end_time = end_time or time.time()
        self.duration = duration or (self.end_time - self.start_time)
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert the task result to a dictionary
        
        Returns:
            Dict[str, Any]: Dictionary representation of the task result
        """
        return {
            "id": self.id,
            "status": self.status.value,
            "result": self.result,
            "error": self.error,
            "start_time": self.start_time,
            "end_time": self.end_time,
            "duration": self.duration,
        }

class ConcurrentExecutionEngine:
    """
    Concurrent execution engine for the Codegen agent
    
    This class provides a concurrent execution engine for the Codegen agent,
    allowing for parallel execution of tasks.
    """
    
    @inject
    def __init__(
        self,
        app: TaskWeaverApp,
        config: AppConfigSource,
        logger: TelemetryLogger,
        memory: Optional[Memory] = None,
        max_concurrent_tasks: int = 3,
    ) -> None:
        self.app = app
        self.config = config
        self.logger = logger
        self.memory = memory or Memory()
        
        # Codegen agent
        self.codegen_agent = None
        
        # Task execution
        self.max_concurrent_tasks = max_concurrent_tasks
        self.executor = ThreadPoolExecutor(max_workers=max_concurrent_tasks)
        
        # Task tracking
        self.tasks = {}
        self.task_results = {}
        self.task_lock = threading.Lock()
        self.running_tasks = set()
        self.cancel_event = threading.Event()
    
    def execute_tasks(self, tasks: List[AtomicTask]) -> Dict[str, TaskResult]:
        """
        Execute tasks concurrently
        
        Args:
            tasks: List of tasks to execute
            
        Returns:
            Dict[str, TaskResult]: Results of the tasks
        """
        # Validate parameters
        if not tasks:
            raise ValueError("No tasks provided")
        
        if not self.codegen_agent:
            raise ValueError("Codegen agent not initialized")
        
        # Reset cancel event
        self.cancel_event.clear()
        
        # Create a dependency graph
        dependency_graph = self._create_dependency_graph(tasks)
        
        # Get tasks with no dependencies
        ready_tasks = [task for task in tasks if not dependency_graph.get(task.id, [])]
        
        # Initialize task tracking
        with self.task_lock:
            self.tasks = {task.id: task for task in tasks}
            self.task_results = {}
            self.running_tasks = set()
        
        # Execute tasks
        while ready_tasks or self.running_tasks:
            # Check if cancellation was requested
            if self.cancel_event.is_set():
                self._cancel_running_tasks()
                break
            
            # Start new tasks if possible
            while ready_tasks and len(self.running_tasks) < self.max_concurrent_tasks:
                task = ready_tasks.pop(0)
                self._start_task(task)
            
            # Wait for a task to complete
            time.sleep(0.1)
            
            # Check for completed tasks
            completed_tasks = []
            with self.task_lock:
                for task_id in list(self.running_tasks):
                    if task_id in self.task_results and self.task_results[task_id].status != TaskStatus.RUNNING:
                        completed_tasks.append(task_id)
                        self.running_tasks.remove(task_id)
            
            # Update ready tasks based on completed tasks
            for task_id in completed_tasks:
                # Find tasks that depend on this task
                for dependent_task_id, dependencies in dependency_graph.items():
                    if task_id in dependencies:
                        dependencies.remove(task_id)
                        # If all dependencies are satisfied, add to ready tasks
                        if not dependencies and dependent_task_id in self.tasks:
                            ready_tasks.append(self.tasks[dependent_task_id])
        
        # Return results
        with self.task_lock:
            return self.task_results.copy()
    
    async def execute_tasks_async(self, tasks: List[AtomicTask]) -> Dict[str, TaskResult]:
        """
        Execute tasks concurrently using asyncio
        
        Args:
            tasks: List of tasks to execute
            
        Returns:
            Dict[str, TaskResult]: Results of the tasks
        """
        # Validate parameters
        if not tasks:
            raise ValueError("No tasks provided")
        
        if not self.codegen_agent:
            raise ValueError("Codegen agent not initialized")
        
        # Reset cancel event
        self.cancel_event.clear()
        
        # Create a dependency graph
        dependency_graph = self._create_dependency_graph(tasks)
        
        # Get tasks with no dependencies
        ready_tasks = [task for task in tasks if not dependency_graph.get(task.id, [])]
        
        # Initialize task tracking
        with self.task_lock:
            self.tasks = {task.id: task for task in tasks}
            self.task_results = {}
            self.running_tasks = set()
        
        # Create a queue for completed tasks
        completed_queue = asyncio.Queue()
        
        # Execute tasks
        async def execute_task(task):
            result = self._execute_task(task)
            await completed_queue.put(task.id)
            return result
        
        # Main execution loop
        running_tasks = set()
        while ready_tasks or running_tasks:
            # Check if cancellation was requested
            if self.cancel_event.is_set():
                # Cancel running tasks
                for task_id in running_tasks:
                    with self.task_lock:
                        if task_id in self.running_tasks:
                            self.running_tasks.remove(task_id)
                break
            
            # Start new tasks if possible
            while ready_tasks and len(running_tasks) < self.max_concurrent_tasks:
                task = ready_tasks.pop(0)
                task_id = task.id
                running_tasks.add(task_id)
                with self.task_lock:
                    self.running_tasks.add(task_id)
                asyncio.create_task(execute_task(task))
            
            # Wait for a task to complete
            try:
                completed_task_id = await asyncio.wait_for(completed_queue.get(), 0.1)
                running_tasks.remove(completed_task_id)
                
                # Find tasks that depend on this task
                for dependent_task_id, dependencies in dependency_graph.items():
                    if completed_task_id in dependencies:
                        dependencies.remove(completed_task_id)
                        # If all dependencies are satisfied, add to ready tasks
                        if not dependencies and dependent_task_id in self.tasks:
                            ready_tasks.append(self.tasks[dependent_task_id])
            except asyncio.TimeoutError:
                # No task completed in the timeout period
                await asyncio.sleep(0.1)
        
        # Return results
        with self.task_lock:
            return self.task_results.copy()
    
    def execute_single_task(self, task: AtomicTask) -> TaskResult:
        """
        Execute a single task
        
        Args:
            task: Task to execute
            
        Returns:
            TaskResult: Result of the task
        """
        # Validate parameters
        if not task:
            raise ValueError("No task provided")
        
        if not self.codegen_agent:
            raise ValueError("Codegen agent not initialized")
        
        # Execute the task
        return self._execute_task(task)
    
    def _execute_task(self, task: AtomicTask) -> TaskResult:
        """
        Execute a task and update the task results
        
        Args:
            task: Task to execute
            
        Returns:
            TaskResult: Result of the task
        """
        task_id = task.id
        
        # Create a task result with running status
        result = TaskResult(
            id=task_id,
            status=TaskStatus.RUNNING,
            start_time=time.time(),
            end_time=None,
            duration=None
        )
        
        # Update task results
        with self.task_lock:
            self.task_results[task_id] = result
        
        try:
            # Create a prompt for the task
            prompt = self._create_task_prompt(task)
            
            # Execute the task using the Codegen agent
            codegen_task = self.codegen_agent.create_task(prompt=prompt)
            
            # Wait for the task to complete
            max_retries = 30
            for i in range(max_retries):
                # Check if cancellation was requested
                if self.cancel_event.is_set():
                    # Update task result
                    result.status = TaskStatus.CANCELLED
                    result.end_time = time.time()
                    result.duration = result.end_time - result.start_time
                    
                    # Update task results
                    with self.task_lock:
                        self.task_results[task_id] = result
                    
                    return result
                
                # Refresh the task status
                codegen_task.refresh()
                
                # Check if the task is completed
                if codegen_task.status == "completed":
                    # Update task result
                    result.status = TaskStatus.COMPLETED
                    result.result = codegen_task.result
                    result.end_time = time.time()
                    result.duration = result.end_time - result.start_time
                    
                    # Update task results
                    with self.task_lock:
                        self.task_results[task_id] = result
                    
                    return result
                elif codegen_task.status in ["failed", "cancelled"]:
                    # Update task result
                    result.status = TaskStatus.FAILED
                    result.error = f"Codegen task failed: {codegen_task.status}"
                    result.end_time = time.time()
                    result.duration = result.end_time - result.start_time
                    
                    # Update task results
                    with self.task_lock:
                        self.task_results[task_id] = result
                    
                    return result
                
                # Wait before checking again
                time.sleep(5)
            
            # Task timed out
            result.status = TaskStatus.FAILED
            result.error = "Task timed out"
            result.end_time = time.time()
            result.duration = result.end_time - result.start_time
            
            # Update task results
            with self.task_lock:
                self.task_results[task_id] = result
            
            return result
        except Exception as e:
            # Update task result
            result.status = TaskStatus.FAILED
            result.error = str(e)
            result.end_time = time.time()
            result.duration = result.end_time - result.start_time
            
            # Update task results
            with self.task_lock:
                self.task_results[task_id] = result
            
            # Log the error
            logger.error(f"Error executing task {task_id}: {str(e)}", exc_info=True)
            
            return result
    
    def _start_task(self, task: AtomicTask) -> None:
        """
        Start a task in a separate thread
        
        Args:
            task: Task to start
        """
        task_id = task.id
        
        # Add to running tasks
        with self.task_lock:
            self.running_tasks.add(task_id)
        
        # Submit the task to the executor
        self.executor.submit(self._execute_task, task)
    
    def _create_dependency_graph(self, tasks: List[AtomicTask]) -> Dict[str, Set[str]]:
        """
        Create a dependency graph for the tasks
        
        Args:
            tasks: List of tasks
            
        Returns:
            Dict[str, Set[str]]: Dependency graph
        """
        dependency_graph = {}
        
        # Create a map of task IDs to tasks
        task_map = {task.id: task for task in tasks}
        
        # Create the dependency graph
        for task in tasks:
            dependencies = set()
            
            # Add explicit dependencies
            for dependency_id in task.dependencies:
                if dependency_id in task_map:
                    dependencies.add(dependency_id)
            
            # Add the dependencies to the graph
            dependency_graph[task.id] = dependencies
        
        return dependency_graph
    
    def _create_task_prompt(self, task: AtomicTask) -> str:
        """
        Create a prompt for a task
        
        Args:
            task: Task to create a prompt for
            
        Returns:
            str: Prompt for the task
        """
        # Create a prompt template
        prompt_template = f"""
# Task: {task.title}

## Description
{task.description}

## Requirements
- Implement the functionality described in the task
- Ensure the code is well-documented
- Handle edge cases and errors appropriately
- Follow best practices for the language and framework

## Context
- Task ID: {task.id}
- Priority: {task.priority}
- Phase: {task.phase}
- Tags: {', '.join(task.tags) if task.tags else 'None'}

Please provide a complete implementation for this task.
"""
        
        return prompt_template
    
    def _cancel_running_tasks(self) -> None:
        """
        Cancel all running tasks
        """
        with self.task_lock:
            for task_id in self.running_tasks:
                if task_id in self.task_results:
                    result = self.task_results[task_id]
                    result.status = TaskStatus.CANCELLED
                    result.end_time = time.time()
                    result.duration = result.end_time - result.start_time
            
            self.running_tasks = set()
    
    def cancel_all_tasks(self) -> bool:
        """
        Cancel all running tasks
        
        Returns:
            bool: True if cancellation was successful, False otherwise
        """
        try:
            # Set the cancel event
            self.cancel_event.set()
            
            # Wait for tasks to be cancelled
            max_wait = 10  # seconds
            start_time = time.time()
            while self.running_tasks and time.time() - start_time < max_wait:
                time.sleep(0.1)
            
            # Force cancel any remaining tasks
            self._cancel_running_tasks()
            
            return True
        except Exception as e:
            logger.error(f"Error cancelling tasks: {str(e)}", exc_info=True)
            return False
    
    def get_task_status(self, task_id: str) -> Dict[str, Any]:
        """
        Get the status of a task
        
        Args:
            task_id: ID of the task
            
        Returns:
            Dict[str, Any]: Status of the task
        """
        with self.task_lock:
            if task_id in self.task_results:
                result = self.task_results[task_id]
                return {
                    "id": result.id,
                    "status": result.status.value,
                    "start_time": result.start_time,
                    "end_time": result.end_time,
                    "duration": result.duration,
                }
        
        return {
            "id": task_id,
            "status": "not_found",
        }
    
    def get_task_result(self, task_id: str) -> Dict[str, Any]:
        """
        Get the result of a task
        
        Args:
            task_id: ID of the task
            
        Returns:
            Dict[str, Any]: Result of the task
        """
        with self.task_lock:
            if task_id in self.task_results:
                return self.task_results[task_id].to_dict()
        
        return {
            "id": task_id,
            "status": "not_found",
        }
    
    def get_status(self) -> Dict[str, Any]:
        """
        Get the status of the execution engine
        
        Returns:
            Dict[str, Any]: Status of the execution engine
        """
        with self.task_lock:
            return {
                "running_tasks": len(self.running_tasks),
                "total_tasks": len(self.tasks),
                "completed_tasks": sum(1 for result in self.task_results.values() if result.status == TaskStatus.COMPLETED),
                "failed_tasks": sum(1 for result in self.task_results.values() if result.status == TaskStatus.FAILED),
                "cancelled_tasks": sum(1 for result in self.task_results.values() if result.status == TaskStatus.CANCELLED),
            }
