#!/usr/bin/env python3
"""
Enhanced TaskWeaver UI class with multithreaded execution support
"""

import os
import json
import logging
import threading
import asyncio
from typing import Dict, List, Optional, Any, Union, Tuple

from injector import inject

from standalone_taskweaver.app.app import TaskWeaverApp
from standalone_taskweaver.config.config_mgt import AppConfigSource
from standalone_taskweaver.logging import TelemetryLogger
from standalone_taskweaver.codegen_agent.codegen_agent import CodegenAgent
from standalone_taskweaver.codegen_agent.requirements_manager import RequirementsManager
from standalone_taskweaver.codegen_agent.concurrent_context_manager import ConcurrentContextManager
from standalone_taskweaver.codegen_agent.concurrent_execution import ConcurrentExecutionEngine

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("taskweaver-ui-enhanced")

class TaskWeaverUIEnhanced:
    """
    Enhanced TaskWeaver UI class with multithreaded execution support
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
        
        # Initialize components
        self.requirements_manager = RequirementsManager(app, config, logger)
        self.context_manager = ConcurrentContextManager(app, config, logger)
        self.execution_engine = ConcurrentExecutionEngine(app, config, logger)
        self.codegen_agent = CodegenAgent(
            app, 
            config, 
            logger, 
            self.requirements_manager,
            self.context_manager,
            self.execution_engine
        )
        
        # Chat history
        self.chat_history = []
        
        # Project context
        self.project_name = None
        self.project_description = None
        self.requirements_text = None
        
        # Execution status
        self.is_executing = False
        self.execution_thread = None
        self.execution_results = {}
        
        # Initialize components
        self.requirements_manager.initialize()
        self.context_manager.initialize()
        
    def initialize_agent(self, codegen_token: str) -> bool:
        """
        Initialize the Codegen agent with the provided token
        
        Args:
            codegen_token: Codegen API token
            
        Returns:
            bool: True if initialization was successful, False otherwise
        """
        return self.codegen_agent.initialize(codegen_token)
    
    def add_message(self, role: str, content: str) -> None:
        """
        Add a message to the chat history
        
        Args:
            role: Role of the message sender (user or assistant)
            content: Content of the message
        """
        self.chat_history.append({
            "role": role,
            "content": content,
            "timestamp": self.app.get_current_time_str()
        })
        
        # If this is a user message, update requirements
        if role == "user":
            self._update_requirements_from_chat()
    
    def _update_requirements_from_chat(self) -> None:
        """
        Update requirements based on the chat history
        """
        # Extract requirements from chat history
        requirements_text = ""
        for message in self.chat_history:
            if message["role"] == "user":
                requirements_text += message["content"] + "\n\n"
        
        self.requirements_text = requirements_text
    
    def set_project_context(
        self, 
        project_name: str, 
        project_description: str
    ) -> None:
        """
        Set the project context
        
        Args:
            project_name: Name of the project
            project_description: Description of the project
        """
        self.project_name = project_name
        self.project_description = project_description
        
        # Update Codegen agent context
        if self.requirements_text:
            self.codegen_agent.set_project_context(
                project_name=project_name,
                project_description=project_description,
                requirements_text=self.requirements_text
            )
    
    def get_requirements(self) -> Dict[str, Any]:
        """
        Get the current requirements
        
        Returns:
            Dict[str, Any]: Current requirements
        """
        return {
            "text": self.requirements_text,
            "tasks": self.requirements_manager.get_atomic_tasks_dict(),
            "dependency_graph": self.requirements_manager.get_dependency_graph_dict()
        }
    
    def execute_tasks(self, max_concurrent_tasks: int = 3) -> None:
        """
        Execute tasks based on the requirements
        
        Args:
            max_concurrent_tasks: Maximum number of concurrent tasks to execute
        """
        if self.is_executing:
            logger.warning("Tasks are already being executed")
            return
        
        self.is_executing = True
        
        # Start execution in a separate thread
        self.execution_thread = threading.Thread(
            target=self._execute_tasks_thread,
            args=(max_concurrent_tasks,)
        )
        self.execution_thread.daemon = True
        self.execution_thread.start()
    
    def _execute_tasks_thread(self, max_concurrent_tasks: int) -> None:
        """
        Thread function for executing tasks
        
        Args:
            max_concurrent_tasks: Maximum number of concurrent tasks to execute
        """
        try:
            # Execute tasks
            results = self.codegen_agent.execute_tasks(max_concurrent_tasks)
            
            # Store results
            self.execution_results = results
        except Exception as e:
            logger.error(f"Error executing tasks: {str(e)}")
        finally:
            self.is_executing = False
    
    async def execute_tasks_async(self, max_concurrent_tasks: int = 3) -> Dict[str, Any]:
        """
        Execute tasks asynchronously based on the requirements
        
        Args:
            max_concurrent_tasks: Maximum number of concurrent tasks to execute
            
        Returns:
            Dict[str, Any]: Results of the task execution
        """
        if self.is_executing:
            logger.warning("Tasks are already being executed")
            return {"error": "Tasks are already being executed"}
        
        self.is_executing = True
        
        try:
            # Execute tasks asynchronously
            results = await self.codegen_agent.execute_tasks_async(max_concurrent_tasks)
            
            # Store results
            self.execution_results = results
            
            return results
        except Exception as e:
            logger.error(f"Error executing tasks asynchronously: {str(e)}")
            return {"error": str(e)}
        finally:
            self.is_executing = False
    
    def get_execution_status(self) -> Dict[str, Any]:
        """
        Get the status of task execution
        
        Returns:
            Dict[str, Any]: Status of task execution
        """
        agent_status = self.codegen_agent.get_status()
        
        return {
            "is_executing": self.is_executing,
            "agent_status": agent_status,
            "results": self.execution_results
        }
    
    def cancel_execution(self) -> bool:
        """
        Cancel the current task execution
        
        Returns:
            bool: True if cancellation was successful, False otherwise
        """
        if not self.is_executing:
            logger.warning("No tasks are being executed")
            return False
        
        # Cancel tasks
        result = self.codegen_agent.cancel_all_tasks()
        
        # Update status
        if result:
            self.is_executing = False
        
        return result
    
    def get_chat_history(self) -> List[Dict[str, Any]]:
        """
        Get the chat history
        
        Returns:
            List[Dict[str, Any]]: Chat history
        """
        return self.chat_history
    
    def clear_chat_history(self) -> None:
        """
        Clear the chat history
        """
        self.chat_history = []
        self.requirements_text = None

