#!/usr/bin/env python3
"""
Query Generation Framework for TaskWeaver-Codegen Integration

This module provides functionality for generating optimized queries for concurrent execution.
"""

import os
import re
import sys
import json
import logging
from typing import Dict, List, Optional, Any, Union, Tuple, Set

from injector import inject

from standalone_taskweaver.app.app import TaskWeaverApp
from standalone_taskweaver.config.config_mgt import AppConfigSource
from standalone_taskweaver.logging import TelemetryLogger
from standalone_taskweaver.codegen_agent.requirements_manager import AtomicTask, DependencyGraph

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
logger = logging.getLogger("query-generation")

class QueryGenerationFramework:
    """
    Generates optimized queries for concurrent execution
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
        self.codegen_agent = None
        
    def initialize(self, org_id: str, token: str) -> None:
        """
        Initialize the Codegen agent
        
        Args:
            org_id: Codegen organization ID
            token: Codegen API token
        """
        self.codegen_agent = Agent(org_id=org_id, token=token)
        logger.info("Initialized Codegen agent")
        
    def generate_queries(self, requirements: List[str], phase: int = 1) -> List[str]:
        """
        Generate optimized queries for a specific phase
        
        Args:
            requirements: List of requirements
            phase: Phase number (default: 1)
            
        Returns:
            List of queries
        """
        # Generate queries
        queries = []
        for requirement in requirements:
            query = f"Implement the following requirement (Phase {phase}): {requirement}"
            queries.append(query)
            
        # Optimize queries for concurrency
        optimized_queries = self.optimize_for_concurrency(queries)
        
        return optimized_queries
        
    def generate_queries_from_tasks(self, tasks: List[AtomicTask], phase: int = 1) -> List[str]:
        """
        Generate optimized queries from atomic tasks for a specific phase
        
        Args:
            tasks: List of atomic tasks
            phase: Phase number (default: 1)
            
        Returns:
            List of queries
        """
        # Filter tasks by phase
        phase_tasks = [task for task in tasks if task.phase == phase]
        
        # Generate queries
        queries = []
        for task in phase_tasks:
            query = f"Implement {task.title}"
            if task.description:
                query += f": {task.description}"
                
            # Add dependencies information
            if task.dependencies:
                query += f" (Dependencies: {', '.join(task.dependencies)})"
                
            # Add tags information
            if task.tags:
                query += f" (Tags: {', '.join(task.tags)})"
                
            queries.append(query)
            
        # Optimize queries for concurrency
        optimized_queries = self.optimize_for_concurrency(queries)
        
        return optimized_queries
        
    def optimize_for_concurrency(self, queries: List[str]) -> List[str]:
        """
        Optimize queries for maximum concurrency
        
        Args:
            queries: List of queries
            
        Returns:
            Optimized list of queries
        """
        # Add context to each query to make it self-contained
        optimized_queries = []
        for query in queries:
            optimized_query = f"[SELF-CONTAINED TASK] {query}"
            optimized_queries.append(optimized_query)
            
        return optimized_queries
        
    def generate_interface_queries(self, tasks: List[AtomicTask]) -> List[str]:
        """
        Generate queries for interface definitions
        
        Args:
            tasks: List of atomic tasks
            
        Returns:
            List of queries
        """
        # Filter tasks that need interfaces
        interface_tasks = [task for task in tasks if any(keyword in task.title.lower() for keyword in ["api", "interface", "component", "service", "module"])]
        
        # Generate queries
        queries = []
        for task in interface_tasks:
            query = f"Define the interface for {task.title}"
            if task.description:
                query += f": {task.description}"
                
            queries.append(query)
            
        # Optimize queries for concurrency
        optimized_queries = self.optimize_for_concurrency(queries)
        
        return optimized_queries
        
    def generate_mock_implementation_queries(self, interface_tasks: List[AtomicTask]) -> List[str]:
        """
        Generate queries for mock implementations
        
        Args:
            interface_tasks: List of interface tasks
            
        Returns:
            List of queries
        """
        # Generate queries
        queries = []
        for task in interface_tasks:
            query = f"Create a mock implementation for {task.title}"
            if task.description:
                query += f": {task.description}"
                
            queries.append(query)
            
        # Optimize queries for concurrency
        optimized_queries = self.optimize_for_concurrency(queries)
        
        return optimized_queries
        
    def generate_validation_contract_queries(self, interface_tasks: List[AtomicTask]) -> List[str]:
        """
        Generate queries for validation contracts
        
        Args:
            interface_tasks: List of interface tasks
            
        Returns:
            List of queries
        """
        # Generate queries
        queries = []
        for task in interface_tasks:
            query = f"Define validation contracts for {task.title}"
            if task.description:
                query += f": {task.description}"
                
            queries.append(query)
            
        # Optimize queries for concurrency
        optimized_queries = self.optimize_for_concurrency(queries)
        
        return optimized_queries
        
    def generate_data_format_queries(self, interface_tasks: List[AtomicTask]) -> List[str]:
        """
        Generate queries for data format standards
        
        Args:
            interface_tasks: List of interface tasks
            
        Returns:
            List of queries
        """
        # Generate queries
        queries = []
        for task in interface_tasks:
            query = f"Define data format standards for {task.title}"
            if task.description:
                query += f": {task.description}"
                
            queries.append(query)
            
        # Optimize queries for concurrency
        optimized_queries = self.optimize_for_concurrency(queries)
        
        return optimized_queries
        
    def generate_api_contract_queries(self, interface_tasks: List[AtomicTask]) -> List[str]:
        """
        Generate queries for API contracts
        
        Args:
            interface_tasks: List of interface tasks
            
        Returns:
            List of queries
        """
        # Generate queries
        queries = []
        for task in interface_tasks:
            query = f"Document API contracts for {task.title}"
            if task.description:
                query += f": {task.description}"
                
            queries.append(query)
            
        # Optimize queries for concurrency
        optimized_queries = self.optimize_for_concurrency(queries)
        
        return optimized_queries
        
    def execute_query(self, query: str) -> str:
        """
        Execute a query using the Codegen API
        
        Args:
            query: Query string
            
        Returns:
            Result string
        """
        if not self.codegen_agent:
            raise ValueError("Codegen agent not initialized. Call initialize() first.")
            
        # Execute the task using the Codegen SDK
        task = self.codegen_agent.run(prompt=query)
        
        # Wait for the task to complete
        while task.status not in ["completed", "failed", "cancelled"]:
            # Refresh the task status
            task.refresh()
            
            # Wait a bit before checking again
            import time
            time.sleep(5)
            
        # Return the result
        if task.status == "completed":
            return task.result
        else:
            raise Exception(f"Failed to execute query: {task.error}")
            
    def execute_queries(self, queries: List[str]) -> List[str]:
        """
        Execute multiple queries using the Codegen API
        
        Args:
            queries: List of query strings
            
        Returns:
            List of result strings
        """
        if not self.codegen_agent:
            raise ValueError("Codegen agent not initialized. Call initialize() first.")
            
        # Execute each query
        results = []
        for query in queries:
            try:
                result = self.execute_query(query)
                results.append(result)
            except Exception as e:
                logger.error(f"Error executing query: {e}")
                results.append(f"Error: {e}")
                
        return results
        
    def execute_queries_concurrently(self, queries: List[str]) -> List[str]:
        """
        Execute multiple queries concurrently using the Codegen API
        
        Args:
            queries: List of query strings
            
        Returns:
            List of result strings
        """
        if not self.codegen_agent:
            raise ValueError("Codegen agent not initialized. Call initialize() first.")
            
        # Execute each query concurrently
        tasks = []
        for query in queries:
            task = self.codegen_agent.run(prompt=query)
            tasks.append(task)
            
        # Wait for all tasks to complete
        results = []
        for task in tasks:
            # Wait for the task to complete
            while task.status not in ["completed", "failed", "cancelled"]:
                # Refresh the task status
                task.refresh()
                
                # Wait a bit before checking again
                import time
                time.sleep(5)
                
            # Add the result
            if task.status == "completed":
                results.append(task.result)
            else:
                results.append(f"Error: {task.error}")
                
        return results
        
    def generate_phase_plan(self, dependency_graph: DependencyGraph) -> List[List[str]]:
        """
        Generate a plan for executing tasks in phases
        
        Args:
            dependency_graph: Dependency graph
            
        Returns:
            List of phases, each containing a list of task IDs
        """
        # Get phases from the graph
        phases = dependency_graph.get_phases()
        
        # Log the plan
        logger.info(f"Generated phase plan with {len(phases)} phases")
        for i, phase in enumerate(phases):
            logger.info(f"Phase {i+1}: {len(phase)} tasks")
            
        return phases
        
    def balance_workload(self, tasks: List[AtomicTask], max_tasks_per_batch: int = 5) -> List[List[AtomicTask]]:
        """
        Balance the workload by grouping tasks into batches
        
        Args:
            tasks: List of atomic tasks
            max_tasks_per_batch: Maximum number of tasks per batch
            
        Returns:
            List of batches, each containing a list of tasks
        """
        # Sort tasks by estimated time (descending)
        sorted_tasks = sorted(tasks, key=lambda t: t.estimated_time, reverse=True)
        
        # Group tasks into batches
        batches = []
        current_batch = []
        current_batch_time = 0
        
        for task in sorted_tasks:
            # If adding this task would exceed the max tasks per batch,
            # or if the batch is already full, start a new batch
            if len(current_batch) >= max_tasks_per_batch:
                batches.append(current_batch)
                current_batch = [task]
                current_batch_time = task.estimated_time
            else:
                current_batch.append(task)
                current_batch_time += task.estimated_time
                
        # Add the last batch if it's not empty
        if current_batch:
            batches.append(current_batch)
            
        # Log the batches
        logger.info(f"Balanced workload into {len(batches)} batches")
        for i, batch in enumerate(batches):
            logger.info(f"Batch {i+1}: {len(batch)} tasks, {sum(t.estimated_time for t in batch)} minutes")
            
        return batches
        
    def identify_critical_path(self, dependency_graph: DependencyGraph) -> List[str]:
        """
        Identify the critical path through the dependency graph
        
        Args:
            dependency_graph: Dependency graph
            
        Returns:
            List of task IDs on the critical path
        """
        # Get the critical path
        critical_path = dependency_graph.get_critical_path()
        
        # Log the critical path
        logger.info(f"Identified critical path with {len(critical_path)} tasks")
        logger.info(f"Critical path: {critical_path}")
        
        return critical_path
        
    def prioritize_critical_path(self, tasks: List[AtomicTask], critical_path: List[str]) -> List[AtomicTask]:
        """
        Prioritize tasks on the critical path
        
        Args:
            tasks: List of atomic tasks
            critical_path: List of task IDs on the critical path
            
        Returns:
            Prioritized list of tasks
        """
        # Increase the priority of tasks on the critical path
        for task in tasks:
            if task.id in critical_path:
                task.priority += 10
                
        # Sort tasks by priority (descending)
        sorted_tasks = sorted(tasks, key=lambda t: t.priority, reverse=True)
        
        return sorted_tasks
        
    def add_forward_looking_context(self, queries: List[str], dependency_graph: DependencyGraph) -> List[str]:
        """
        Add forward-looking context to queries
        
        Args:
            queries: List of queries
            dependency_graph: Dependency graph
            
        Returns:
            List of queries with forward-looking context
        """
        # Add forward-looking context to each query
        enhanced_queries = []
        
        for query in queries:
            # Extract task ID from the query
            task_id_match = re.search(r'\b(TASK-\d+)\b', query)
            if not task_id_match:
                # If no task ID found, just add the query as is
                enhanced_queries.append(query)
                continue
                
            task_id = task_id_match.group(1)
            
            # Get dependents of this task
            dependents = dependency_graph.get_dependents(task_id)
            
            if dependents:
                # Add information about dependents
                dependent_tasks = [dependency_graph.get_task(dep_id) for dep_id in dependents]
                dependent_info = ", ".join([f"{task.id}: {task.title}" for task in dependent_tasks if task])
                
                # Add forward-looking context
                enhanced_query = f"{query}\n\nThis component will be used by: {dependent_info}"
                enhanced_queries.append(enhanced_query)
            else:
                # No dependents, add the query as is
                enhanced_queries.append(query)
                
        return enhanced_queries

