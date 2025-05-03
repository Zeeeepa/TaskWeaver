#!/usr/bin/env python3
"""
Codegen Agent Implementation

This module provides the main implementation of the Codegen agent, which
supports multithreaded requests to the Codegen API while referencing
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
from standalone_taskweaver.memory import Memory
from standalone_taskweaver.codegen_agent.requirements_manager import RequirementsManager, AtomicTask, DependencyGraph
from standalone_taskweaver.codegen_agent.concurrent_execution import ConcurrentExecutionEngine, TaskStatus, TaskResult
from standalone_taskweaver.codegen_agent.concurrent_context_manager import ConcurrentContextManager
from standalone_taskweaver.codegen_agent.utils import initialize_codegen_client, safe_execute, validate_required_params

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("codegen-agent")

class CodegenAgentStatus(Enum):
    """
    Status of the Codegen agent
    """
    UNINITIALIZED = "uninitialized"
    INITIALIZING = "initializing"
    READY = "ready"
    BUSY = "busy"
    ERROR = "error"

class CodegenAgent:
    """
    Codegen agent implementation
    
    This class provides the main implementation of the Codegen agent, which
    supports multithreaded requests to the Codegen API while referencing
    project requirements and context.
    """
    
    @inject
    def __init__(
        self,
        app: TaskWeaverApp,
        config: AppConfigSource,
        logger: TelemetryLogger,
        memory: Optional[Memory] = None,
    ) -> None:
        self.app = app
        self.config = config
        self.logger = logger
        self.memory = memory or Memory()
        
        # Codegen agent
        self.codegen_agent = None
        self.codegen_client = None
        
        # Status
        self.status = CodegenAgentStatus.UNINITIALIZED
        
        # Project context
        self.project_name = None
        self.project_description = None
        self.requirements_text = None
        
        # Execution engine
        self.execution_engine = ConcurrentExecutionEngine(
            app=app,
            config=config,
            logger=logger
        )
        
        # Context manager
        self.context_manager = ConcurrentContextManager(
            app=app,
            config=config,
            logger=logger,
            memory=self.memory
        )
    
    def initialize(self, codegen_token: str) -> bool:
        """
        Initialize the Codegen agent with the provided token

        Args:
            codegen_token: Codegen API token

        Returns:
            bool: True if initialization was successful, False otherwise
            
        Raises:
            ValueError: If the token is empty or invalid
            ImportError: If the Codegen SDK is not installed
        """
        if not codegen_token or not isinstance(codegen_token, str) or not codegen_token.strip():
            self.logger.error("Invalid Codegen token provided: token cannot be empty")
            self.status = CodegenAgentStatus.ERROR
            return False
            
        try:
            self.status = CodegenAgentStatus.INITIALIZING
            
            # Initialize the Codegen agent
            self.codegen_agent = initialize_codegen_client(codegen_token)
            
            if not self.codegen_agent:
                self.status = CodegenAgentStatus.ERROR
                self.logger.error("Failed to initialize Codegen agent: client initialization returned None")
                return False
            
            # Initialize the Codegen client
            try:
                from codegen.extensions.events.client import CodegenClient
                self.codegen_client = CodegenClient(token=codegen_token)
                self.logger.info("Codegen client initialized successfully")
            except ImportError as e:
                self.logger.warning(f"CodegenClient not available: {str(e)}. Some features may not work.")
                self.codegen_client = None
            except Exception as e:
                self.logger.warning(f"Failed to initialize CodegenClient: {str(e)}. Some features may not work.")
                self.codegen_client = None
            
            # Initialize the execution engine
            self.execution_engine.codegen_agent = self.codegen_agent
            
            # Update status
            self.status = CodegenAgentStatus.READY
            self.logger.info("Codegen agent initialized successfully")
            
            return True
        except ImportError as e:
            self.logger.error(f"Failed to import required modules: {str(e)}", exc_info=True)
            self.status = CodegenAgentStatus.ERROR
            return False
        except Exception as e:
            self.logger.error(f"Failed to initialize Codegen agent: {str(e)}", exc_info=True)
            self.status = CodegenAgentStatus.ERROR
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
        # Validate parameters
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
        
        # Set project context
        self.project_name = project_name
        self.project_description = project_description
        self.requirements_text = requirements_text
        
        # Update context manager
        self.context_manager.set_project_context(
            project_name=project_name,
            project_description=project_description,
            requirements_text=requirements_text
        )
    
    def execute_tasks(self, max_concurrent_tasks: int = 3) -> Dict[str, Any]:
        """
        Execute tasks based on the project context
        
        Args:
            max_concurrent_tasks: Maximum number of concurrent tasks
            
        Returns:
            Dict[str, Any]: Results of the tasks
        """
        if self.status != CodegenAgentStatus.READY:
            raise ValueError("Codegen agent not initialized or not ready")
        
        try:
            self.status = CodegenAgentStatus.BUSY
            
            # Create tasks from requirements
            requirements_manager = RequirementsManager(
                app=self.app,
                config=self.config,
                logger=self.logger,
                codegen_integration=None
            )
            
            tasks = requirements_manager.create_atomic_tasks_from_requirements(
                self.requirements_text
            )
            
            # Execute tasks
            results = self.execution_engine.execute_tasks(tasks)
            
            # Update status
            self.status = CodegenAgentStatus.READY
            
            return results
        except Exception as e:
            self.logger.error(f"Error executing tasks: {str(e)}", exc_info=True)
            self.status = CodegenAgentStatus.ERROR
            return {"error": str(e)}
    
    async def execute_tasks_async(self, max_concurrent_tasks: int = 3) -> Dict[str, Any]:
        """
        Execute tasks asynchronously based on the project context
        
        Args:
            max_concurrent_tasks: Maximum number of concurrent tasks
            
        Returns:
            Dict[str, Any]: Results of the tasks
        """
        if self.status != CodegenAgentStatus.READY:
            raise ValueError("Codegen agent not initialized or not ready")
        
        try:
            self.status = CodegenAgentStatus.BUSY
            
            # Create tasks from requirements
            requirements_manager = RequirementsManager(
                app=self.app,
                config=self.config,
                logger=self.logger,
                codegen_integration=None
            )
            
            tasks = requirements_manager.create_atomic_tasks_from_requirements(
                self.requirements_text
            )
            
            # Execute tasks asynchronously
            results = await self.execution_engine.execute_tasks_async(tasks)
            
            # Update status
            self.status = CodegenAgentStatus.READY
            
            return results
        except Exception as e:
            self.logger.error(f"Error executing tasks asynchronously: {str(e)}", exc_info=True)
            self.status = CodegenAgentStatus.ERROR
            return {"error": str(e)}
    
    def execute_single_task(self, task: AtomicTask) -> TaskResult:
        """
        Execute a single task
        
        Args:
            task: Task to execute
            
        Returns:
            TaskResult: Result of the task
        """
        if self.status != CodegenAgentStatus.READY:
            raise ValueError("Codegen agent not initialized or not ready")
        
        try:
            # Execute the task
            result = self.execution_engine.execute_single_task(task)
            
            return result
        except Exception as e:
            self.logger.error(f"Error executing task: {str(e)}", exc_info=True)
            return TaskResult(
                id=task.id,
                status=TaskStatus.FAILED,
                result=None,
                error=str(e),
                start_time=time.time(),
                end_time=time.time(),
                duration=0
            )
    
    def get_task_status(self, task_id: str) -> Dict[str, Any]:
        """
        Get the status of a task
        
        Args:
            task_id: ID of the task
            
        Returns:
            Dict[str, Any]: Status of the task
        """
        return self.execution_engine.get_task_status(task_id)
    
    def get_task_result(self, task_id: str) -> Dict[str, Any]:
        """
        Get the result of a task
        
        Args:
            task_id: ID of the task
            
        Returns:
            Dict[str, Any]: Result of the task
        """
        return self.execution_engine.get_task_result(task_id)
    
    def cancel_all_tasks(self) -> bool:
        """
        Cancel all running tasks
        
        Returns:
            bool: True if cancellation was successful, False otherwise
        """
        return self.execution_engine.cancel_all_tasks()
    
    def get_status(self) -> Dict[str, Any]:
        """
        Get the status of the Codegen agent
        
        Returns:
            Dict[str, Any]: Status of the Codegen agent
        """
        return {
            "status": self.status.value,
            "project_name": self.project_name,
            "project_description": self.project_description,
            "execution_engine": self.execution_engine.get_status()
        }
