#!/usr/bin/env python3
"""
Example of concurrent execution with TaskWeaver-Codegen integration
"""

import os
import sys
import json
import asyncio
import logging
from pathlib import Path

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent.parent.parent))

from standalone_taskweaver.codegen_agent.requirements_manager import RequirementsManager, AtomicTask, DependencyGraph
from standalone_taskweaver.codegen_agent.concurrent_execution import ConcurrentExecutionEngine
from standalone_taskweaver.codegen_agent.interface_generator import InterfaceGenerator
from standalone_taskweaver.codegen_agent.query_generation import QueryGenerationFramework

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("concurrent-execution-example")

async def main():
    """Main function"""
    # Check if Codegen API credentials are provided
    if len(sys.argv) < 3:
        print("Usage: python concurrent_execution_example.py <org_id> <token>")
        return
        
    org_id = sys.argv[1]
    token = sys.argv[2]
    
    # Create a requirements manager
    requirements_manager = RequirementsManager(None, None, None)
    
    # Create a REQUIREMENTS.md file
    requirements_manager.create_requirements_file()
    
    # Create a STRUCTURE.md file
    requirements_manager.create_structure_file()
    
    # Create some example tasks
    tasks = [
        AtomicTask(
            id="TASK-1",
            title="Create a user authentication module",
            description="Implement a user authentication module with login, logout, and registration functionality",
            priority=1,
            dependencies=[],
            phase=1,
            status="pending",
            tags=["authentication", "user"],
            estimated_time=60,
            assignee=None,
            interface_definition=False,
        ),
        AtomicTask(
            id="TASK-2",
            title="Create a database connection module",
            description="Implement a database connection module with CRUD operations",
            priority=1,
            dependencies=[],
            phase=1,
            status="pending",
            tags=["database", "connection"],
            estimated_time=45,
            assignee=None,
            interface_definition=False,
        ),
        AtomicTask(
            id="TASK-3",
            title="Create a user profile module",
            description="Implement a user profile module with profile viewing and editing functionality",
            priority=2,
            dependencies=["TASK-1", "TASK-2"],
            phase=2,
            status="pending",
            tags=["profile", "user"],
            estimated_time=90,
            assignee=None,
            interface_definition=False,
        ),
    ]
    
    # Identify dependencies
    graph = requirements_manager.identify_dependencies(tasks)
    
    # Prioritize tasks
    phases = requirements_manager.prioritize_tasks(graph)
    
    print(f"Tasks grouped into {len(phases)} phases:")
    for i, phase in enumerate(phases):
        print(f"Phase {i+1}:")
        for task in phase:
            print(f"  {task.id}: {task.title}")
        print()
        
    # Generate interfaces for components
    interface_generator = InterfaceGenerator(None, None, None)
    interface_generator.initialize(org_id, token)
    
    print("Generating interfaces for components...")
    interfaces = {}
    for task in tasks:
        if any(keyword in task.title.lower() for keyword in ["module", "component", "service"]):
            # Extract component name
            import re
            component_match = re.search(r'\b([A-Z][a-z]+(?:[A-Z][a-z]+)*)\b', task.title)
            
            if component_match:
                component_name = component_match.group(1)
                
                # Create component specification
                component_spec = {
                    "name": component_name,
                    "description": task.description,
                    "task_id": task.id,
                }
                
                # Generate interface
                print(f"Generating interface for {component_name}...")
                interface = interface_generator.generate_interface(component_spec)
                
                # Store the interface
                interfaces[component_name] = interface
                
                # Print the interface
                print(f"Interface for {component_name}:")
                print(interface[:500] + "..." if len(interface) > 500 else interface)
                print()
                
    # Create mock implementations for interfaces
    print("Creating mock implementations for interfaces...")
    mock_implementations = {}
    for component_name, interface in interfaces.items():
        # Create mock implementation
        print(f"Creating mock implementation for {component_name}...")
        mock = interface_generator.create_mock_implementation(interface)
        
        # Store the mock implementation
        mock_implementations[component_name] = mock
        
        # Print the mock implementation
        print(f"Mock implementation for {component_name}:")
        print(mock[:500] + "..." if len(mock) > 500 else mock)
        print()
        
    # Generate queries for tasks
    query_generation_framework = QueryGenerationFramework(None, None, None)
    query_generation_framework.initialize(org_id, token)
    
    print("Generating queries for tasks...")
    queries = query_generation_framework.generate_queries_from_tasks(tasks, phase=1)
    
    print(f"Generated {len(queries)} queries:")
    for query in queries:
        print(query)
        print()
        
    # Execute queries concurrently
    print("Executing queries concurrently...")
    results = query_generation_framework.execute_queries_concurrently(queries[:2])  # Only execute the first 2 queries
    
    print(f"Executed {len(results)} queries:")
    for i, result in enumerate(results):
        print(f"Result {i+1}:")
        print(result[:500] + "..." if len(result) > 500 else result)
        print()
        
    # Execute tasks concurrently
    concurrent_execution_engine = ConcurrentExecutionEngine(None, None, None, max_concurrency=2)
    concurrent_execution_engine.initialize(org_id, token)
    
    print("Executing tasks concurrently...")
    phase_1_tasks = [task for task in tasks if task.phase == 1]
    task_results = await concurrent_execution_engine.execute_tasks(phase_1_tasks)
    
    print(f"Executed {len(task_results)} tasks:")
    for result in task_results:
        print(f"Task {result.task_id}: {result.status.value}")
        if result.error:
            print(f"  Error: {result.error}")
        if result.result:
            print(f"  Result: {result.result[:500]}...")
        print(f"  Duration: {result.duration:.2f} seconds")
        print()
        
if __name__ == "__main__":
    asyncio.run(main())

