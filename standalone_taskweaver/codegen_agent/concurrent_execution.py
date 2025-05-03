#!/usr/bin/env python3
"""
Concurrent execution engine for TaskWeaver-Codegen integration
"""

import time
import asyncio
import logging
from typing import Dict, List, Optional, Any, Union, Tuple
from concurrent.futures import ThreadPoolExecutor

from injector import inject

from standalone_taskweaver.app.app import TaskWeaverApp
from standalone_taskweaver.config.config_mgt import AppConfigSource
from standalone_taskweaver.logging import TelemetryLogger
from standalone_taskweaver.codegen_agent.requirements_manager import AtomicTask

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("concurrent-execution-engine")

class TaskResult:
    """
    Result of a task execution
    """
    
    def __init__(
        self,
        task_id: str,
        codegen_task_id: str = "",
        status: str = "pending",
        start_time: float = 0,
        end_time: float = 0,
        result: Any = None,
        error: Exception = None,
    ) -> None:
        self.task_id = task_id
        self.codegen_task_id = codegen_task_id
        self.status = status
        self.start_time = start_time
        self.end_time = end_time
        self.duration = end_time - start_time if end_time > 0 else 0
        self.result = result
        self.error = error
        
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "task_id": self.task_id,
            "codegen_task_id": self.codegen_task_id,
            "status": self.status,
            "start_time": self.start_time,
            "end_time": self.end_time,
            "duration": self.duration,
            "result": self.result,
            "error": str(self.error) if self.error else None,
        }

class TaskStatus:
    """
    Task status constants
    """
    
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"

class ConcurrentExecutionEngine:
    """
    Engine for concurrent execution of tasks
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
        self.codegen_org_id = None
        self.codegen_token = None
        self.codegen_agent = None
        self.max_concurrent_tasks = 5
        self.tasks = {}
        
    def initialize(self, codegen_org_id: str, codegen_token: str) -> None:
        """
        Initialize the concurrent execution engine with Codegen credentials
        
        Args:
            codegen_org_id: Codegen organization ID
            codegen_token: Codegen API token
        """
        self.codegen_org_id = codegen_org_id
        self.codegen_token = codegen_token
        self.logger.info("Concurrent execution engine initialized")
        
        # Initialize Codegen agent
        # This is a placeholder - actual implementation would depend on the Codegen SDK
        self.codegen_agent = None
        
    def _create_prompt(self, task: AtomicTask) -> str:
        """
        Create a prompt for a task
        
        Args:
            task: Atomic task
            
        Returns:
            Prompt string
        """
        prompt = f"# Task: {task.title}\n\n"
        prompt += f"## Description\n{task.description}\n\n"
        
        if task.dependencies:
            prompt += f"## Dependencies\n"
            for dep_id in task.dependencies:
                prompt += f"- {dep_id}\n"
            prompt += "\n"
            
        if task.tags:
            prompt += f"## Tags\n"
            for tag in task.tags:
                prompt += f"- {tag}\n"
            prompt += "\n"
            
        return prompt
        
    async def execute_tasks(self, tasks: List[AtomicTask]) -> List[TaskResult]:
        """
        Execute multiple tasks concurrently and return results
        
        Args:
            tasks: List of atomic tasks
            
        Returns:
            List of task results
        """
        if not self.codegen_org_id or not self.codegen_token:
            raise ValueError("Concurrent execution engine not initialized. Call initialize() first.")
            
        # Create a semaphore to limit concurrent tasks
        semaphore = asyncio.Semaphore(self.max_concurrent_tasks)
        
        # Create a list of tasks to execute
        task_futures = []
        for task in tasks:
            task_futures.append(self._execute_task(task, semaphore))
            
        # Wait for all tasks to complete
        results = await asyncio.gather(*task_futures)
        
        return results
        
    async def _execute_task(self, task: AtomicTask, semaphore: asyncio.Semaphore) -> TaskResult:
        """
        Execute a single task
        
        Args:
            task: Atomic task
            semaphore: Semaphore to limit concurrent tasks
            
        Returns:
            Task result
        """
        async with semaphore:
            task_result = TaskResult(
                task_id=task.id,
                codegen_task_id="",
                status=TaskStatus.RUNNING,
                start_time=time.time(),
            )
            self.tasks[task.id] = task_result
            
            try:
                # Create prompt
                prompt = self._create_prompt(task)
                
                # Execute task using Codegen agent
                # This is a placeholder - actual implementation would depend on the Codegen SDK
                codegen_task = None
                
                if self.codegen_agent:
                    codegen_task = self.codegen_agent.run(prompt=prompt)
                    task_result.codegen_task_id = codegen_task.id
                    
                    # Poll for task completion
                    while codegen_task.status not in ["completed", "failed", "cancelled"]:
                        # Refresh task status
                        codegen_task.refresh()
                        
                        # Wait before polling again
                        await asyncio.sleep(5)
                        
                    # Update task result
                    if codegen_task.status == "completed":
                        task_result.status = TaskStatus.COMPLETED
                        task_result.result = codegen_task.result
                    elif codegen_task.status == "failed":
                        task_result.status = TaskStatus.FAILED
                        task_result.error = Exception(f"Codegen task failed: {codegen_task.error}")
                    elif codegen_task.status == "cancelled":
                        task_result.status = TaskStatus.CANCELLED
                        task_result.error = Exception("Codegen task cancelled")
                else:
                    # Simulate task execution
                    await asyncio.sleep(2)
                    task_result.status = TaskStatus.COMPLETED
                    task_result.result = f"Simulated result for task {task.id}"
                    
            except Exception as e:
                task_result.status = TaskStatus.FAILED
                task_result.error = e
                self.logger.error(f"Error executing task {task.id}: {e}")
                
            finally:
                task_result.end_time = time.time()
                task_result.duration = task_result.end_time - task_result.start_time
                
            return task_result
            
    def execute_task_sync(self, task: AtomicTask) -> TaskResult:
        """
        Execute a task synchronously
        
        Args:
            task: Atomic task
            
        Returns:
            Task result
        """
        if not self.codegen_org_id or not self.codegen_token:
            raise ValueError("Concurrent execution engine not initialized. Call initialize() first.")
            
        task_result = TaskResult(
            task_id=task.id,
            codegen_task_id="",
            status=TaskStatus.RUNNING,
            start_time=time.time(),
        )
        self.tasks[task.id] = task_result
        
        try:
            # Create prompt
            prompt = self._create_prompt(task)
            
            # Execute task using Codegen agent
            # This is a placeholder - actual implementation would depend on the Codegen SDK
            codegen_task = None
            
            if self.codegen_agent:
                codegen_task = self.codegen_agent.run(prompt=prompt)
                task_result.codegen_task_id = codegen_task.id
                
                # Poll for task completion
                for _ in range(30):  # Maximum 30 retries
                    # Refresh task status
                    codegen_task.refresh()
                    
                    if codegen_task.status in ["completed", "failed", "cancelled"]:
                        break
                        
                    # Wait before polling again
                    time.sleep(5)
                    
                # Update task result
                if codegen_task.status == "completed":
                    task_result.status = TaskStatus.COMPLETED
                    task_result.result = codegen_task.result
                elif codegen_task.status == "failed":
                    task_result.status = TaskStatus.FAILED
                    task_result.error = Exception(f"Codegen task failed: {codegen_task.error}")
                elif codegen_task.status == "cancelled":
                    task_result.status = TaskStatus.CANCELLED
                    task_result.error = Exception("Codegen task cancelled")
                else:
                    task_result.status = TaskStatus.FAILED
                    task_result.error = Exception("Codegen task timed out")
            else:
                # Simulate task execution
                time.sleep(2)
                task_result.status = TaskStatus.COMPLETED
                task_result.result = f"Simulated result for task {task.id}"
                
        except Exception as e:
            task_result.status = TaskStatus.FAILED
            task_result.error = e
            self.logger.error(f"Error executing task {task.id}: {e}")
            
        finally:
            task_result.end_time = time.time()
            task_result.duration = task_result.end_time - task_result.start_time
            
        return task_result
        
    def execute_tasks_sync(self, tasks: List[AtomicTask]) -> List[TaskResult]:
        """
        Execute multiple tasks synchronously and return results
        
        Args:
            tasks: List of atomic tasks
            
        Returns:
            List of task results
        """
        if not self.codegen_org_id or not self.codegen_token:
            raise ValueError("Concurrent execution engine not initialized. Call initialize() first.")
            
        results = []
        
        for task in tasks:
            result = self.execute_task_sync(task)
            results.append(result)
            
        return results
        
    def execute_tasks_parallel(self, tasks: List[AtomicTask], max_workers: int = None) -> List[TaskResult]:
        """
        Execute multiple tasks in parallel using a thread pool
        
        Args:
            tasks: List of atomic tasks
            max_workers: Maximum number of worker threads
            
        Returns:
            List of task results
        """
        if not self.codegen_org_id or not self.codegen_token:
            raise ValueError("Concurrent execution engine not initialized. Call initialize() first.")
            
        if max_workers is None:
            max_workers = min(len(tasks), self.max_concurrent_tasks)
            
        results = []
        
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = {executor.submit(self.execute_task_sync, task): task for task in tasks}
            
            for future in futures:
                try:
                    result = future.result()
                    results.append(result)
                except Exception as e:
                    task = futures[future]
                    self.logger.error(f"Error executing task {task.id}: {e}")
                    results.append(TaskResult(
                        task_id=task.id,
                        status=TaskStatus.FAILED,
                        error=e,
                    ))
                    
        return results
        
    async def monitor_progress(self, task_ids: List[str]) -> Dict[str, Any]:
        """
        Monitor progress of multiple concurrent tasks
        
        Args:
            task_ids: List of task IDs
            
        Returns:
            Dictionary mapping task IDs to statuses
        """
        if not self.codegen_org_id or not self.codegen_token:
            raise ValueError("Concurrent execution engine not initialized. Call initialize() first.")
            
        progress = {}
        
        for task_id in task_ids:
            if task_id in self.tasks:
                task_result = self.tasks[task_id]
                progress[task_id] = task_result.to_dict()
            else:
                progress[task_id] = {"status": "unknown"}
                
        return progress
        
    def get_task_result(self, task_id: str) -> Optional[TaskResult]:
        """
        Get the result of a task
        
        Args:
            task_id: Task ID
            
        Returns:
            Task result if found, None otherwise
        """
        return self.tasks.get(task_id)
        
    def get_all_task_results(self) -> Dict[str, TaskResult]:
        """
        Get all task results
        
        Returns:
            Dictionary mapping task IDs to task results
        """
        return self.tasks
        
    def cancel_task(self, task_id: str) -> bool:
        """
        Cancel a task
        
        Args:
            task_id: Task ID
            
        Returns:
            True if successful, False otherwise
        """
        if task_id not in self.tasks:
            return False
            
        task_result = self.tasks[task_id]
        
        if task_result.status in [TaskStatus.COMPLETED, TaskStatus.FAILED, TaskStatus.CANCELLED]:
            return False
            
        # Cancel the task
        task_result.status = TaskStatus.CANCELLED
        task_result.end_time = time.time()
        task_result.duration = task_result.end_time - task_result.start_time
        task_result.error = Exception("Task cancelled")
        
        # Cancel the Codegen task if it exists
        if task_result.codegen_task_id and self.codegen_agent:
            try:
                # This is a placeholder - actual implementation would depend on the Codegen SDK
                pass
            except Exception as e:
                self.logger.error(f"Error cancelling Codegen task {task_result.codegen_task_id}: {e}")
                
        return True
        
    def cancel_all_tasks(self) -> int:
        """
        Cancel all running tasks
        
        Returns:
            Number of tasks cancelled
        """
        cancelled_count = 0
        
        for task_id in self.tasks:
            if self.cancel_task(task_id):
                cancelled_count += 1
                
        return cancelled_count

