#!/usr/bin/env python3
"""
Concurrent Context Manager for TaskWeaver-Codegen Integration

This module provides an enhanced context manager that supports concurrent operations
and maintains isolated contexts for different tasks.
"""

import os
import sys
import json
import logging
from typing import Dict, List, Optional, Any, Union, Tuple, Set
from pathlib import Path

from injector import inject

from standalone_taskweaver.app.app import TaskWeaverApp
from standalone_taskweaver.config.config_mgt import AppConfigSource
from standalone_taskweaver.logging import TelemetryLogger
from standalone_taskweaver.memory import Memory
from standalone_taskweaver.codegen_agent.bidirectional_context import BidirectionalContext

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("concurrent-context-manager")

class TaskContext:
    """
    Represents an isolated context for a specific task
    """
    
    def __init__(self, task_id: str) -> None:
        self.task_id = task_id
        self.context_data = {
            "task_id": task_id,
            "metadata": {},
            "files": {},
            "codebase": {},
            "requirements": {},
            "interfaces": {},
            "dependencies": {},
        }
        
    def add_metadata(self, key: str, value: Any) -> None:
        """Add metadata to the context"""
        self.context_data["metadata"][key] = value
        
    def add_file(self, file_path: str, content: str) -> None:
        """Add a file to the context"""
        self.context_data["files"][file_path] = content
        
    def add_codebase_info(self, key: str, value: Any) -> None:
        """Add codebase information to the context"""
        self.context_data["codebase"][key] = value
        
    def add_requirement(self, req_id: str, requirement: Dict[str, Any]) -> None:
        """Add a requirement to the context"""
        self.context_data["requirements"][req_id] = requirement
        
    def add_interface(self, interface_id: str, interface: Dict[str, Any]) -> None:
        """Add an interface to the context"""
        self.context_data["interfaces"][interface_id] = interface
        
    def add_dependency(self, dep_id: str, dependency: Dict[str, Any]) -> None:
        """Add a dependency to the context"""
        self.context_data["dependencies"][dep_id] = dependency
        
    def get_metadata(self, key: str) -> Any:
        """Get metadata from the context"""
        return self.context_data["metadata"].get(key)
        
    def get_file(self, file_path: str) -> Optional[str]:
        """Get a file from the context"""
        return self.context_data["files"].get(file_path)
        
    def get_codebase_info(self, key: str) -> Any:
        """Get codebase information from the context"""
        return self.context_data["codebase"].get(key)
        
    def get_requirement(self, req_id: str) -> Optional[Dict[str, Any]]:
        """Get a requirement from the context"""
        return self.context_data["requirements"].get(req_id)
        
    def get_interface(self, interface_id: str) -> Optional[Dict[str, Any]]:
        """Get an interface from the context"""
        return self.context_data["interfaces"].get(interface_id)
        
    def get_dependency(self, dep_id: str) -> Optional[Dict[str, Any]]:
        """Get a dependency from the context"""
        return self.context_data["dependencies"].get(dep_id)
        
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return self.context_data
        
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'TaskContext':
        """Create from dictionary"""
        task_id = data.get("task_id", "unknown")
        context = cls(task_id)
        context.context_data = data
        return context

class ConcurrentContextManager(BidirectionalContext):
    """
    Enhanced context manager supporting concurrent operations
    """
    
    @inject
    def __init__(
        self,
        app: TaskWeaverApp,
        config: AppConfigSource,
        logger: TelemetryLogger,
        memory: Memory,
    ) -> None:
        super().__init__(app, config, logger, memory)
        self.task_contexts = {}  # task_id -> TaskContext
        
    def create_isolated_context(self, task_id: str) -> TaskContext:
        """
        Create an isolated context for a specific task
        
        Args:
            task_id: Task ID
            
        Returns:
            Task context
        """
        # Create a new task context
        context = TaskContext(task_id)
        
        # Add basic metadata
        context.add_metadata("created_at", self._get_timestamp())
        context.add_metadata("task_id", task_id)
        
        # Store the context
        self.task_contexts[task_id] = context
        
        return context
        
    def _get_timestamp(self) -> str:
        """Get the current timestamp"""
        import datetime
        return datetime.datetime.now().isoformat()
        
    def get_task_context(self, task_id: str) -> Optional[TaskContext]:
        """
        Get the context for a specific task
        
        Args:
            task_id: Task ID
            
        Returns:
            Task context or None if not found
        """
        return self.task_contexts.get(task_id)
        
    def merge_contexts(self, contexts: List[TaskContext]) -> BidirectionalContext:
        """
        Merge multiple task contexts into a unified context
        
        Args:
            contexts: List of task contexts
            
        Returns:
            Merged bidirectional context
        """
        # Create a new bidirectional context
        merged_context = BidirectionalContext(self.app, self.config, self.logger, self.memory)
        
        # Merge metadata
        metadata = {}
        for context in contexts:
            metadata.update(context.context_data["metadata"])
        
        # Merge files
        files = {}
        for context in contexts:
            files.update(context.context_data["files"])
        
        # Merge codebase info
        codebase = {}
        for context in contexts:
            codebase.update(context.context_data["codebase"])
        
        # Merge requirements
        requirements = {}
        for context in contexts:
            requirements.update(context.context_data["requirements"])
        
        # Merge interfaces
        interfaces = {}
        for context in contexts:
            interfaces.update(context.context_data["interfaces"])
        
        # Merge dependencies
        dependencies = {}
        for context in contexts:
            dependencies.update(context.context_data["dependencies"])
        
        # Update the merged context
        merged_context.update_taskweaver_context({
            "metadata": metadata,
            "files": files,
            "codebase": codebase,
            "requirements": requirements,
            "interfaces": interfaces,
            "dependencies": dependencies,
        })
        
        return merged_context
        
    def export_task_context(self, task_id: str, output_path: str) -> None:
        """
        Export a task context to a JSON file
        
        Args:
            task_id: Task ID
            output_path: Path to the output file
        """
        context = self.get_task_context(task_id)
        if not context:
            raise ValueError(f"Task context not found for task ID: {task_id}")
            
        with open(output_path, "w") as f:
            json.dump(context.to_dict(), f, indent=2)
            
        logger.info(f"Exported task context for task {task_id} to {output_path}")
        
    def import_task_context(self, input_path: str) -> TaskContext:
        """
        Import a task context from a JSON file
        
        Args:
            input_path: Path to the input file
            
        Returns:
            Task context
        """
        with open(input_path, "r") as f:
            data = json.load(f)
            
        context = TaskContext.from_dict(data)
        
        # Store the context
        self.task_contexts[context.task_id] = context
        
        logger.info(f"Imported task context for task {context.task_id} from {input_path}")
        
        return context
        
    def add_file_to_task_context(self, task_id: str, file_path: str) -> None:
        """
        Add a file to a task context
        
        Args:
            task_id: Task ID
            file_path: Path to the file
        """
        context = self.get_task_context(task_id)
        if not context:
            raise ValueError(f"Task context not found for task ID: {task_id}")
            
        # Read the file
        with open(file_path, "r") as f:
            content = f.read()
            
        # Add the file to the context
        context.add_file(file_path, content)
        
        logger.info(f"Added file {file_path} to task context for task {task_id}")
        
    def add_requirement_to_task_context(self, task_id: str, req_id: str, requirement: Dict[str, Any]) -> None:
        """
        Add a requirement to a task context
        
        Args:
            task_id: Task ID
            req_id: Requirement ID
            requirement: Requirement data
        """
        context = self.get_task_context(task_id)
        if not context:
            raise ValueError(f"Task context not found for task ID: {task_id}")
            
        # Add the requirement to the context
        context.add_requirement(req_id, requirement)
        
        logger.info(f"Added requirement {req_id} to task context for task {task_id}")
        
    def add_interface_to_task_context(self, task_id: str, interface_id: str, interface: Dict[str, Any]) -> None:
        """
        Add an interface to a task context
        
        Args:
            task_id: Task ID
            interface_id: Interface ID
            interface: Interface data
        """
        context = self.get_task_context(task_id)
        if not context:
            raise ValueError(f"Task context not found for task ID: {task_id}")
            
        # Add the interface to the context
        context.add_interface(interface_id, interface)
        
        logger.info(f"Added interface {interface_id} to task context for task {task_id}")
        
    def add_dependency_to_task_context(self, task_id: str, dep_id: str, dependency: Dict[str, Any]) -> None:
        """
        Add a dependency to a task context
        
        Args:
            task_id: Task ID
            dep_id: Dependency ID
            dependency: Dependency data
        """
        context = self.get_task_context(task_id)
        if not context:
            raise ValueError(f"Task context not found for task ID: {task_id}")
            
        # Add the dependency to the context
        context.add_dependency(dep_id, dependency)
        
        logger.info(f"Added dependency {dep_id} to task context for task {task_id}")
        
    def export_all_task_contexts(self, output_dir: str) -> None:
        """
        Export all task contexts to JSON files
        
        Args:
            output_dir: Path to the output directory
        """
        # Create the output directory if it doesn't exist
        os.makedirs(output_dir, exist_ok=True)
        
        # Export each task context
        for task_id, context in self.task_contexts.items():
            output_path = os.path.join(output_dir, f"{task_id}.json")
            self.export_task_context(task_id, output_path)
            
        logger.info(f"Exported all task contexts to {output_dir}")
        
    def import_all_task_contexts(self, input_dir: str) -> None:
        """
        Import all task contexts from JSON files
        
        Args:
            input_dir: Path to the input directory
        """
        # Get all JSON files in the input directory
        json_files = [f for f in os.listdir(input_dir) if f.endswith(".json")]
        
        # Import each task context
        for json_file in json_files:
            input_path = os.path.join(input_dir, json_file)
            self.import_task_context(input_path)
            
        logger.info(f"Imported all task contexts from {input_dir}")
        
    def clear_task_context(self, task_id: str) -> None:
        """
        Clear a task context
        
        Args:
            task_id: Task ID
        """
        if task_id in self.task_contexts:
            del self.task_contexts[task_id]
            logger.info(f"Cleared task context for task {task_id}")
        else:
            logger.warning(f"Task context not found for task ID: {task_id}")
            
    def clear_all_task_contexts(self) -> None:
        """Clear all task contexts"""
        self.task_contexts.clear()
        logger.info("Cleared all task contexts")

