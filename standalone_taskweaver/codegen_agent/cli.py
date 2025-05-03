#!/usr/bin/env python3
"""
Command-Line Interface for TaskWeaver-Codegen Integration

This module provides a command-line interface for the TaskWeaver-Codegen integration,
allowing users to create, parse, and manage requirements, execute tasks concurrently,
and generate interfaces.
"""

import os
import sys
import json
import argparse
import asyncio
import logging
from typing import Dict, List, Optional, Any, Union, Tuple

from standalone_taskweaver.codegen_agent.integration import CodegenIntegration
from standalone_taskweaver.codegen_agent.requirements_manager import RequirementsManager, AtomicTask, DependencyGraph
from standalone_taskweaver.codegen_agent.concurrent_execution import ConcurrentExecutionEngine, ErrorHandlingFramework
from standalone_taskweaver.codegen_agent.interface_generator import InterfaceGenerator
from standalone_taskweaver.codegen_agent.concurrent_context_manager import ConcurrentContextManager
from standalone_taskweaver.codegen_agent.query_generation import QueryGenerationFramework
from standalone_taskweaver.memory import Memory

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("codegen-cli")

def create_requirements_file(args):
    """Create a REQUIREMENTS.md file"""
    requirements_manager = RequirementsManager(None, None, None)
    
    if args.input_file:
        with open(args.input_file, "r") as f:
            content = f.read()
    else:
        content = None
        
    requirements_manager.create_requirements_file(content)
    
def create_structure_file(args):
    """Create a STRUCTURE.md file"""
    requirements_manager = RequirementsManager(None, None, None)
    
    if args.input_file:
        with open(args.input_file, "r") as f:
            content = f.read()
    else:
        content = None
        
    requirements_manager.create_structure_file(content)
    
def parse_requirements(args):
    """Parse REQUIREMENTS.md into atomic tasks"""
    requirements_manager = RequirementsManager(None, None, None)
    
    tasks = requirements_manager.parse_requirements()
    
    if args.output_file:
        requirements_manager.export_tasks_to_json(tasks, args.output_file)
    else:
        for task in tasks:
            print(f"{task.id}: {task.title}")
            if task.description:
                print(f"  Description: {task.description}")
            if task.dependencies:
                print(f"  Dependencies: {', '.join(task.dependencies)}")
            print()
            
def parse_structure_file(args):
    """Parse STRUCTURE.md to extract requirements section"""
    requirements_manager = RequirementsManager(None, None, None)
    
    structure = requirements_manager.parse_structure_file()
    
    if args.output_file:
        with open(args.output_file, "w") as f:
            json.dump(structure, f, indent=2)
    else:
        print(json.dumps(structure, indent=2))
        
def identify_dependencies(args):
    """Identify dependencies between tasks and create a dependency graph"""
    requirements_manager = RequirementsManager(None, None, None)
    
    if args.input_file:
        tasks = requirements_manager.import_tasks_from_json(args.input_file)
    else:
        tasks = requirements_manager.parse_requirements()
        
    graph = requirements_manager.identify_dependencies(tasks)
    
    if args.output_file:
        with open(args.output_file, "w") as f:
            json.dump(graph.to_dict(), f, indent=2)
    else:
        print(json.dumps(graph.to_dict(), indent=2))
        
def prioritize_tasks(args):
    """Group tasks into phases based on dependencies, maximizing concurrency"""
    requirements_manager = RequirementsManager(None, None, None)
    
    if args.input_file:
        graph_data = json.load(open(args.input_file, "r"))
        tasks = [AtomicTask.from_dict(task_data) for task_data in graph_data["tasks"]]
        graph = DependencyGraph(tasks)
    else:
        tasks = requirements_manager.parse_requirements()
        graph = requirements_manager.identify_dependencies(tasks)
        
    phases = requirements_manager.prioritize_tasks(graph)
    
    if args.output_file:
        with open(args.output_file, "w") as f:
            json.dump([[task.to_dict() for task in phase] for phase in phases], f, indent=2)
    else:
        for i, phase in enumerate(phases):
            print(f"Phase {i+1}:")
            for task in phase:
                print(f"  {task.id}: {task.title}")
            print()
            
def generate_queries(args):
    """Generate optimized queries for a specific phase"""
    requirements_manager = RequirementsManager(None, None, None)
    query_generation_framework = QueryGenerationFramework(None, None, None)
    
    if args.input_file:
        tasks = requirements_manager.import_tasks_from_json(args.input_file)
    else:
        tasks = requirements_manager.parse_requirements()
        
    phase = args.phase or 1
    
    queries = query_generation_framework.generate_queries_from_tasks(tasks, phase)
    
    if args.output_file:
        with open(args.output_file, "w") as f:
            json.dump(queries, f, indent=2)
    else:
        for query in queries:
            print(query)
            print()
            
def execute_queries(args):
    """Execute queries using the Codegen API"""
    query_generation_framework = QueryGenerationFramework(None, None, None)
    
    if not args.org_id or not args.token:
        print("Error: Codegen organization ID and API token are required")
        return
        
    query_generation_framework.initialize(args.org_id, args.token)
    
    if args.input_file:
        with open(args.input_file, "r") as f:
            queries = json.load(f)
    else:
        print("Error: Input file with queries is required")
        return
        
    if args.concurrent:
        results = query_generation_framework.execute_queries_concurrently(queries)
    else:
        results = query_generation_framework.execute_queries(queries)
        
    if args.output_file:
        with open(args.output_file, "w") as f:
            json.dump(results, f, indent=2)
    else:
        for i, result in enumerate(results):
            print(f"Result {i+1}:")
            print(result)
            print()
            
def generate_interface(args):
    """Generate interface definition for a component"""
    interface_generator = InterfaceGenerator(None, None, None)
    
    if not args.org_id or not args.token:
        print("Error: Codegen organization ID and API token are required")
        return
        
    interface_generator.initialize(args.org_id, args.token)
    
    if args.input_file:
        with open(args.input_file, "r") as f:
            component_spec = json.load(f)
    else:
        component_spec = {
            "name": args.name,
            "description": args.description,
        }
        
    interface = interface_generator.generate_interface(component_spec)
    
    if args.output_file:
        with open(args.output_file, "w") as f:
            f.write(interface)
    else:
        print(interface)
        
def create_mock_implementation(args):
    """Create mock implementation for an interface"""
    interface_generator = InterfaceGenerator(None, None, None)
    
    if not args.org_id or not args.token:
        print("Error: Codegen organization ID and API token are required")
        return
        
    interface_generator.initialize(args.org_id, args.token)
    
    if args.input_file:
        with open(args.input_file, "r") as f:
            interface = f.read()
    else:
        print("Error: Input file with interface definition is required")
        return
        
    mock = interface_generator.create_mock_implementation(interface)
    
    if args.output_file:
        with open(args.output_file, "w") as f:
            f.write(mock)
    else:
        print(mock)
        
async def execute_tasks(args):
    """Execute multiple tasks concurrently"""
    requirements_manager = RequirementsManager(None, None, None)
    memory = Memory()
    concurrent_execution_engine = ConcurrentExecutionEngine(None, None, None, memory)
    
    if not args.org_id or not args.token:
        print("Error: Codegen organization ID and API token are required")
        return
        
    concurrent_execution_engine.initialize(args.org_id, args.token)
    
    if args.input_file:
        tasks = requirements_manager.import_tasks_from_json(args.input_file)
    else:
        tasks = requirements_manager.parse_requirements()
        
    results = await concurrent_execution_engine.execute_tasks(tasks)
    
    if args.output_file:
        with open(args.output_file, "w") as f:
            json.dump([result.to_dict() for result in results], f, indent=2)
    else:
        for result in results:
            print(f"Task {result.task_id}: {result.status.value}")
            if result.error:
                print(f"  Error: {result.error}")
            if result.result:
                print(f"  Result: {result.result[:100]}...")
            print(f"  Duration: {result.duration:.2f} seconds")
            print()
            
def main():
    """Main entry point for the CLI"""
    parser = argparse.ArgumentParser(description="TaskWeaver-Codegen Integration CLI")
    subparsers = parser.add_subparsers(dest="command", help="Command to execute")
    
    # Create REQUIREMENTS.md
    create_requirements_parser = subparsers.add_parser("create-requirements", help="Create a REQUIREMENTS.md file")
    create_requirements_parser.add_argument("--input-file", "-i", help="Input file with content for REQUIREMENTS.md")
    create_requirements_parser.set_defaults(func=create_requirements_file)
    
    # Create STRUCTURE.md
    create_structure_parser = subparsers.add_parser("create-structure", help="Create a STRUCTURE.md file")
    create_structure_parser.add_argument("--input-file", "-i", help="Input file with content for STRUCTURE.md")
    create_structure_parser.set_defaults(func=create_structure_file)
    
    # Parse REQUIREMENTS.md
    parse_requirements_parser = subparsers.add_parser("parse-requirements", help="Parse REQUIREMENTS.md into atomic tasks")
    parse_requirements_parser.add_argument("--output-file", "-o", help="Output file for parsed tasks")
    parse_requirements_parser.set_defaults(func=parse_requirements)
    
    # Parse STRUCTURE.md
    parse_structure_parser = subparsers.add_parser("parse-structure", help="Parse STRUCTURE.md to extract requirements section")
    parse_structure_parser.add_argument("--output-file", "-o", help="Output file for parsed structure")
    parse_structure_parser.set_defaults(func=parse_structure_file)
    
    # Identify dependencies
    identify_dependencies_parser = subparsers.add_parser("identify-dependencies", help="Identify dependencies between tasks")
    identify_dependencies_parser.add_argument("--input-file", "-i", help="Input file with tasks")
    identify_dependencies_parser.add_argument("--output-file", "-o", help="Output file for dependency graph")
    identify_dependencies_parser.set_defaults(func=identify_dependencies)
    
    # Prioritize tasks
    prioritize_tasks_parser = subparsers.add_parser("prioritize-tasks", help="Group tasks into phases based on dependencies")
    prioritize_tasks_parser.add_argument("--input-file", "-i", help="Input file with dependency graph")
    prioritize_tasks_parser.add_argument("--output-file", "-o", help="Output file for prioritized tasks")
    prioritize_tasks_parser.set_defaults(func=prioritize_tasks)
    
    # Generate queries
    generate_queries_parser = subparsers.add_parser("generate-queries", help="Generate optimized queries for a specific phase")
    generate_queries_parser.add_argument("--input-file", "-i", help="Input file with tasks")
    generate_queries_parser.add_argument("--output-file", "-o", help="Output file for queries")
    generate_queries_parser.add_argument("--phase", "-p", type=int, help="Phase number (default: 1)")
    generate_queries_parser.set_defaults(func=generate_queries)
    
    # Execute queries
    execute_queries_parser = subparsers.add_parser("execute-queries", help="Execute queries using the Codegen API")
    execute_queries_parser.add_argument("--input-file", "-i", help="Input file with queries")
    execute_queries_parser.add_argument("--output-file", "-o", help="Output file for results")
    execute_queries_parser.add_argument("--org-id", help="Codegen organization ID")
    execute_queries_parser.add_argument("--token", help="Codegen API token")
    execute_queries_parser.add_argument("--concurrent", "-c", action="store_true", help="Execute queries concurrently")
    execute_queries_parser.set_defaults(func=execute_queries)
    
    # Generate interface
    generate_interface_parser = subparsers.add_parser("generate-interface", help="Generate interface definition for a component")
    generate_interface_parser.add_argument("--input-file", "-i", help="Input file with component specification")
    generate_interface_parser.add_argument("--output-file", "-o", help="Output file for interface definition")
    generate_interface_parser.add_argument("--org-id", help="Codegen organization ID")
    generate_interface_parser.add_argument("--token", help="Codegen API token")
    generate_interface_parser.add_argument("--name", help="Component name")
    generate_interface_parser.add_argument("--description", help="Component description")
    generate_interface_parser.set_defaults(func=generate_interface)
    
    # Create mock implementation
    create_mock_parser = subparsers.add_parser("create-mock", help="Create mock implementation for an interface")
    create_mock_parser.add_argument("--input-file", "-i", help="Input file with interface definition")
    create_mock_parser.add_argument("--output-file", "-o", help="Output file for mock implementation")
    create_mock_parser.add_argument("--org-id", help="Codegen organization ID")
    create_mock_parser.add_argument("--token", help="Codegen API token")
    create_mock_parser.set_defaults(func=create_mock_implementation)
    
    # Execute tasks
    execute_tasks_parser = subparsers.add_parser("execute-tasks", help="Execute multiple tasks concurrently")
    execute_tasks_parser.add_argument("--input-file", "-i", help="Input file with tasks")
    execute_tasks_parser.add_argument("--output-file", "-o", help="Output file for results")
    execute_tasks_parser.add_argument("--org-id", help="Codegen organization ID")
    execute_tasks_parser.add_argument("--token", help="Codegen API token")
    execute_tasks_parser.set_defaults(func=lambda args: asyncio.run(execute_tasks(args)))
    
    args = parser.parse_args()
    
    if args.command:
        args.func(args)
    else:
        parser.print_help()
        
if __name__ == "__main__":
    main()
