#!/usr/bin/env python3
"""
Codegen Agent Implementation for TaskWeaver

This module provides a comprehensive implementation of the Codegen agent
that supports multithreaded requests to the Codegen API while referencing
project requirements and context.
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
from standalone_taskweaver.codegen_agent.requirements_manager import RequirementsManager, AtomicTask, DependencyGraph
from standalone_taskweaver.codegen_agent.concurrent_execution import ConcurrentExecutionEngine, TaskStatus, TaskResult
from standalone_taskweaver.codegen_agent.concurrent_context_manager import ConcurrentContextManager

# Import Codegen SDK
try:
    from codegen import Agent
    from codegen.extensions.events.client import CodegenClient
except ImportError:
    print("Codegen SDK not found. Installing...")
    import subprocess
    subprocess.check_call([sys.executable, "-m", "pip", "install", "codegen"])
    from codegen import Agent
    from codegen.extensions.events.client import CodegenClient

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("codegen-agent")

class CodegenAgentStatus(Enum):
    """
    Status of the Codegen agent
    """
    IDLE = "idle"
    INITIALIZING = "initializing"
    RUNNING = "running"
    ERROR = "error"
    COMPLETED = "completed"

class CodegenAgent:
    """
    Codegen Agent Implementation for TaskWeaver
    
    This class provides a comprehensive implementation of the Codegen agent
    that supports multithreaded requests to the Codegen API while referencing
    project requirements and context.
    """
    
    @inject
    def __init__(
        self,
        app: TaskWeaverApp,
        config: AppConfigSource,
        logger: TelemetryLogger,
        requirements_manager: Optional[RequirementsManager] = None,
        context_manager: Optional[ConcurrentContextManager] = None,
        execution_engine: Optional[ConcurrentExecutionEngine] = None,
    ) -> None:
        self.app = app
        self.config = config
        self.logger = logger
        
        # Initialize components
        self.requirements_manager = requirements_manager or RequirementsManager(app, config, logger)
        self.context_manager = context_manager or ConcurrentContextManager(app, config, logger)
        self.execution_engine = execution_engine or ConcurrentExecutionEngine(app, config, logger)
        
        # Codegen client
        self.codegen_client = None
        self.codegen_token = None
        self.agent = None
        
        # Status
        self.status = CodegenAgentStatus.IDLE
        self.error_message = None
        
        # Task tracking
        self.tasks = {}
        self.task_results = {}
        self.task_lock = threading.Lock()
        
        # Project context
        self.project_name = None
        self.project_description = None
        self.requirements_text = None
        
    def initialize(self, codegen_token: str) -> bool:
        """
        Initialize the Codegen agent with the provided token
        
        Args:
            codegen_token: Codegen API token
            
        Returns:
            bool: True if initialization was successful, False otherwise
        """
        try:
            self.status = CodegenAgentStatus.INITIALIZING
            self.codegen_token = codegen_token
            
            # Initialize Codegen client
            self.codegen_client = CodegenClient(base_url="https://api.codegen.sh")
            self.agent = Agent(api_key=codegen_token)
            
            # Initialize components
            self.requirements_manager.initialize()
            self.context_manager.initialize()
            self.execution_engine.initialize(self.agent)
            
            self.status = CodegenAgentStatus.IDLE
            logger.info("Codegen agent initialized successfully")
            return True
        except Exception as e:
            self.status = CodegenAgentStatus.ERROR
            self.error_message = str(e)
            logger.error(f"Failed to initialize Codegen agent: {str(e)}")
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
            requirements_text: Requirements text from the conversation with the user
        """
        self.project_name = project_name
        self.project_description = project_description
        self.requirements_text = requirements_text
        
        # Update context manager
        self.context_manager.set_project_context(
            project_name=project_name,
            project_description=project_description,
            requirements_text=requirements_text
        )
        
        # Parse requirements
        self.requirements_manager.parse_requirements(requirements_text)
        
        logger.info(f"Project context set: {project_name}")
    
    def execute_tasks(self, max_concurrent_tasks: int = 3) -> Dict[str, Any]:
        """
        Execute tasks based on the requirements
        
        Args:
            max_concurrent_tasks: Maximum number of concurrent tasks to execute
            
        Returns:
            Dict[str, Any]: Results of the task execution
        """
        try:
            self.status = CodegenAgentStatus.RUNNING
            
            # Get tasks from requirements manager
            tasks = self.requirements_manager.get_atomic_tasks()
            
            # Set up execution engine
            self.execution_engine.set_max_concurrent_tasks(max_concurrent_tasks)
            self.execution_engine.set_context_manager(self.context_manager)
            
            # Execute tasks
            results = self.execution_engine.execute_tasks(tasks)
            
            # Update task results
            with self.task_lock:
                self.task_results = results
            
            self.status = CodegenAgentStatus.COMPLETED
            return results
        except Exception as e:
            self.status = CodegenAgentStatus.ERROR
            self.error_message = str(e)
            logger.error(f"Failed to execute tasks: {str(e)}")
            return {"error": str(e)}
    
    async def execute_tasks_async(self, max_concurrent_tasks: int = 3) -> Dict[str, Any]:
        """
        Execute tasks asynchronously based on the requirements
        
        Args:
            max_concurrent_tasks: Maximum number of concurrent tasks to execute
            
        Returns:
            Dict[str, Any]: Results of the task execution
        """
        try:
            self.status = CodegenAgentStatus.RUNNING
            
            # Get tasks from requirements manager
            tasks = self.requirements_manager.get_atomic_tasks()
            
            # Set up execution engine
            self.execution_engine.set_max_concurrent_tasks(max_concurrent_tasks)
            self.execution_engine.set_context_manager(self.context_manager)
            
            # Execute tasks asynchronously
            results = await self.execution_engine.execute_tasks_async(tasks)
            
            # Update task results
            with self.task_lock:
                self.task_results = results
            
            self.status = CodegenAgentStatus.COMPLETED
            return results
        except Exception as e:
            self.status = CodegenAgentStatus.ERROR
            self.error_message = str(e)
            logger.error(f"Failed to execute tasks asynchronously: {str(e)}")
            return {"error": str(e)}
    
    def execute_single_task(self, task: AtomicTask) -> TaskResult:
        """
        Execute a single task
        
        Args:
            task: Task to execute
            
        Returns:
            TaskResult: Result of the task execution
        """
        try:
            # Prepare context
            context = self.context_manager.get_context_for_task(task)
            
            # Execute task
            result = self.execution_engine.execute_single_task(task, context)
            
            # Update task results
            with self.task_lock:
                self.task_results[task.id] = result
            
            return result
        except Exception as e:
            logger.error(f"Failed to execute task {task.id}: {str(e)}")
            return TaskResult(
                task_id=task.id,
                status=TaskStatus.FAILED,
                output=None,
                error=str(e),
                execution_time=0
            )
    
    def get_task_status(self, task_id: str) -> Optional[TaskStatus]:
        """
        Get the status of a task
        
        Args:
            task_id: ID of the task
            
        Returns:
            Optional[TaskStatus]: Status of the task, or None if the task is not found
        """
        with self.task_lock:
            if task_id in self.task_results:
                return self.task_results[task_id].status
        return None
    
    def get_task_result(self, task_id: str) -> Optional[TaskResult]:
        """
        Get the result of a task
        
        Args:
            task_id: ID of the task
            
        Returns:
            Optional[TaskResult]: Result of the task, or None if the task is not found
        """
        with self.task_lock:
            if task_id in self.task_results:
                return self.task_results[task_id]
        return None
    
    def get_all_task_results(self) -> Dict[str, TaskResult]:
        """
        Get all task results
        
        Returns:
            Dict[str, TaskResult]: All task results
        """
        with self.task_lock:
            return self.task_results.copy()
    
    def get_status(self) -> Dict[str, Any]:
        """
        Get the status of the Codegen agent
        
        Returns:
            Dict[str, Any]: Status of the Codegen agent
        """
        return {
            "status": self.status.value,
            "error_message": self.error_message,
            "project_name": self.project_name,
            "task_count": len(self.task_results),
            "completed_tasks": sum(1 for result in self.task_results.values() if result.status == TaskStatus.COMPLETED),
            "failed_tasks": sum(1 for result in self.task_results.values() if result.status == TaskStatus.FAILED),
        }
    
    def cancel_all_tasks(self) -> bool:
        """
        Cancel all running tasks
        
        Returns:
            bool: True if cancellation was successful, False otherwise
        """
        try:
            self.execution_engine.cancel_all_tasks()
            self.status = CodegenAgentStatus.IDLE
            return True
        except Exception as e:
            logger.error(f"Failed to cancel tasks: {str(e)}")
            return False
