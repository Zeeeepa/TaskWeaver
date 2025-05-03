#!/usr/bin/env python3
"""
Requirements Manager for TaskWeaver-Codegen Integration

This module provides functionality for creating, parsing, and managing REQUIREMENTS.md files,
breaking down requirements into atomic tasks for concurrent execution.
"""

import os
import re
import sys
import json
import logging
from pathlib import Path
from typing import Dict, List, Optional, Any, Union, Tuple, Set

from injector import inject

from standalone_taskweaver.app.app import TaskWeaverApp
from standalone_taskweaver.config.config_mgt import AppConfigSource
from standalone_taskweaver.logging import TelemetryLogger

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("requirements-manager")

class AtomicTask:
    """
    Represents an atomic task that can be executed independently
    """
    
    def __init__(
        self,
        id: str,
        title: str,
        description: str,
        priority: int = 0,
        dependencies: List[str] = None,
        phase: int = 1,
        status: str = "pending",
        tags: List[str] = None,
        estimated_time: int = 0,  # in minutes
        assignee: str = None,
        interface_definition: bool = False,
    ) -> None:
        self.id = id
        self.title = title
        self.description = description
        self.priority = priority
        self.dependencies = dependencies or []
        self.phase = phase
        self.status = status
        self.tags = tags or []
        self.estimated_time = estimated_time
        self.assignee = assignee
        self.interface_definition = interface_definition
        
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "priority": self.priority,
            "dependencies": self.dependencies,
            "phase": self.phase,
            "status": self.status,
            "tags": self.tags,
            "estimated_time": self.estimated_time,
            "assignee": self.assignee,
            "interface_definition": self.interface_definition,
        }
        
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'AtomicTask':
        """Create from dictionary"""
        return cls(
            id=data["id"],
            title=data["title"],
            description=data["description"],
            priority=data.get("priority", 0),
            dependencies=data.get("dependencies", []),
            phase=data.get("phase", 1),
            status=data.get("status", "pending"),
            tags=data.get("tags", []),
            estimated_time=data.get("estimated_time", 0),
            assignee=data.get("assignee", None),
            interface_definition=data.get("interface_definition", False),
        )

class DependencyGraph:
    """
    Represents a dependency graph of atomic tasks
    """
    
    def __init__(self, tasks: List[AtomicTask] = None) -> None:
        self.tasks = tasks or []
        self.task_map = {task.id: task for task in self.tasks}
        self.graph = self._build_graph()
        
    def _build_graph(self) -> Dict[str, List[str]]:
        """Build the dependency graph"""
        graph = {}
        for task in self.tasks:
            graph[task.id] = task.dependencies
        return graph
        
    def add_task(self, task: AtomicTask) -> None:
        """Add a task to the graph"""
        self.tasks.append(task)
        self.task_map[task.id] = task
        self.graph[task.id] = task.dependencies
        
    def remove_task(self, task_id: str) -> None:
        """Remove a task from the graph"""
        if task_id in self.task_map:
            task = self.task_map[task_id]
            self.tasks.remove(task)
            del self.task_map[task_id]
            del self.graph[task_id]
            
            # Remove task_id from dependencies of other tasks
            for other_task_id, deps in self.graph.items():
                if task_id in deps:
                    self.graph[other_task_id].remove(task_id)
                    self.task_map[other_task_id].dependencies.remove(task_id)
        
    def get_task(self, task_id: str) -> Optional[AtomicTask]:
        """Get a task by ID"""
        return self.task_map.get(task_id)
        
    def get_dependencies(self, task_id: str) -> List[str]:
        """Get dependencies of a task"""
        return self.graph.get(task_id, [])
        
    def get_dependents(self, task_id: str) -> List[str]:
        """Get tasks that depend on this task"""
        dependents = []
        for other_task_id, deps in self.graph.items():
            if task_id in deps:
                dependents.append(other_task_id)
        return dependents
        
    def get_root_tasks(self) -> List[str]:
        """Get tasks with no dependencies"""
        return [task_id for task_id, deps in self.graph.items() if not deps]
        
    def get_leaf_tasks(self) -> List[str]:
        """Get tasks with no dependents"""
        all_task_ids = set(self.graph.keys())
        all_dependents = set()
        for deps in self.graph.values():
            all_dependents.update(deps)
        return list(all_task_ids - all_dependents)
        
    def get_critical_path(self) -> List[str]:
        """Get the critical path through the graph"""
        # Simplified implementation - just returns the longest path
        # A more sophisticated implementation would consider task durations
        longest_path = []
        for root in self.get_root_tasks():
            path = self._get_longest_path_from(root)
            if len(path) > len(longest_path):
                longest_path = path
        return longest_path
        
    def _get_longest_path_from(self, task_id: str) -> List[str]:
        """Get the longest path from a task"""
        if not self.get_dependents(task_id):
            return [task_id]
        
        longest_path = [task_id]
        for dependent in self.get_dependents(task_id):
            path = self._get_longest_path_from(dependent)
            if len(path) + 1 > len(longest_path):
                longest_path = [task_id] + path
        return longest_path
        
    def get_phases(self) -> List[List[str]]:
        """Group tasks into phases based on dependencies"""
        phases = []
        remaining_tasks = set(self.graph.keys())
        
        while remaining_tasks:
            # Tasks with no remaining dependencies
            current_phase = []
            for task_id in list(remaining_tasks):
                if all(dep not in remaining_tasks for dep in self.graph[task_id]):
                    current_phase.append(task_id)
            
            if not current_phase:
                # Circular dependency detected
                logger.warning("Circular dependency detected in the graph")
                break
                
            phases.append(current_phase)
            remaining_tasks -= set(current_phase)
            
        return phases
        
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "tasks": [task.to_dict() for task in self.tasks],
            "graph": self.graph,
        }
        
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'DependencyGraph':
        """Create from dictionary"""
        tasks = [AtomicTask.from_dict(task_data) for task_data in data["tasks"]]
        graph = cls(tasks)
        return graph

class RequirementsManager:
    """
    Manages requirements for TaskWeaver-Codegen integration
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
        self.requirements_path = Path(self.config.app_base_path) / "REQUIREMENTS.md"
        self.structure_path = Path(self.config.app_base_path) / "STRUCTURE.md"
        self.atomic_tasks = []
        self.dependency_graph = None
        
        # Create requirements file if it doesn't exist
        if not os.path.exists(self.requirements_path):
            self.create_requirements_file()
            
        logger.info("Requirements manager initialized")
        
    def create_requirements_file(self, content: str = None) -> None:
        """
        Create a REQUIREMENTS.md file with the given content or a template
        
        Args:
            content: Optional content for the file
        """
        if content is None:
            content = self._get_template()
            
        with open(self.requirements_path, "w") as f:
            f.write(content)
            
        logger.info(f"Created REQUIREMENTS.md at {self.requirements_path}")
        
    def _get_template(self) -> str:
        """Get a template for REQUIREMENTS.md"""
        return """# Project Requirements

## Overview

This document outlines the requirements for the project.

## Functional Requirements

### Core Features

- Feature 1: Description of feature 1
- Feature 2: Description of feature 2
- Feature 3: Description of feature 3

### User Interface

- UI Component 1: Description of UI component 1
- UI Component 2: Description of UI component 2

### Backend

- API Endpoint 1: Description of API endpoint 1
- API Endpoint 2: Description of API endpoint 2

### Database

- Entity 1: Description of entity 1
- Entity 2: Description of entity 2

## Non-Functional Requirements

### Performance

- Performance Requirement 1: Description of performance requirement 1
- Performance Requirement 2: Description of performance requirement 2

### Security

- Security Requirement 1: Description of security requirement 1
- Security Requirement 2: Description of security requirement 2

### Scalability

- Scalability Requirement 1: Description of scalability requirement 1
- Scalability Requirement 2: Description of scalability requirement 2

## Technical Constraints

- Constraint 1: Description of constraint 1
- Constraint 2: Description of constraint 2

## Dependencies

- Dependency 1: Description of dependency 1
- Dependency 2: Description of dependency 2

## Acceptance Criteria

- Criterion 1: Description of criterion 1
- Criterion 2: Description of criterion 2

## Timeline

- Milestone 1: Description of milestone 1
- Milestone 2: Description of milestone 2
"""
        
    def parse_requirements(self) -> List[AtomicTask]:
        """
        Parse REQUIREMENTS.md into atomic tasks
        
        Returns:
            List of atomic tasks
        """
        if not self.requirements_path.exists():
            logger.warning(f"REQUIREMENTS.md not found at {self.requirements_path}")
            return []
            
        with open(self.requirements_path, "r") as f:
            content = f.read()
            
        # Extract requirements using regex
        tasks = []
        
        # Parse section by section
        sections = re.split(r'##\s+', content)
        
        task_id = 1
        
        for section in sections:
            if not section.strip():
                continue
                
            # Get section name and content
            section_lines = section.strip().split('\n')
            section_name = section_lines[0].strip()
            section_content = '\n'.join(section_lines[1:]).strip()
            
            # Extract bullet points
            bullet_points = re.findall(r'[-*]\s+(.*?)(?=\n[-*]|\n\n|$)', section_content, re.DOTALL)
            
            for point in bullet_points:
                point = point.strip()
                if not point:
                    continue
                    
                # Check if it's a feature with description
                if ':' in point:
                    title, description = point.split(':', 1)
                    title = title.strip()
                    description = description.strip()
                else:
                    title = point
                    description = ""
                    
                # Create atomic task
                task = AtomicTask(
                    id=f"TASK-{task_id}",
                    title=title,
                    description=description,
                    tags=[section_name],
                )
                
                tasks.append(task)
                task_id += 1
                
        return tasks
        
    def parse_structure_file(self) -> Dict[str, Any]:
        """
        Parse STRUCTURE.md to extract requirements section
        
        Returns:
            Dictionary with parsed structure
        """
        if not self.structure_path.exists():
            logger.warning(f"STRUCTURE.md not found at {self.structure_path}")
            return {}
            
        with open(self.structure_path, "r") as f:
            content = f.read()
            
        # Extract requirements section
        requirements_section = re.search(r'#{1,6}\s+REQUIREMENTS\s+#{1,6}(.*?)(?=#{1,6}|$)', content, re.DOTALL)
        
        if not requirements_section:
            logger.warning("Requirements section not found in STRUCTURE.md")
            return {}
            
        requirements_content = requirements_section.group(1).strip()
        
        # Parse requirements content
        structure = {
            "requirements": requirements_content,
            "sections": {},
        }
        
        # Extract sections
        sections = re.findall(r'#{1,6}\s+(.*?)\s+#{1,6}(.*?)(?=#{1,6}|$)', content, re.DOTALL)
        
        for section_name, section_content in sections:
            structure["sections"][section_name.strip()] = section_content.strip()
            
        return structure
        
    def create_structure_file(self, content: str = None) -> None:
        """
        Create a STRUCTURE.md file with the given content or a template
        
        Args:
            content: Optional content for the file
        """
        if content is None:
            content = self._get_structure_template()
            
        with open(self.structure_path, "w") as f:
            f.write(content)
            
        logger.info(f"Created STRUCTURE.md at {self.structure_path}")
        
    def _get_structure_template(self) -> str:
        """Get a template for STRUCTURE.md"""
        return """# Project Structure

## Overview

This document outlines the structure of the project.

########## REQUIREMENTS ##########

## Core Principles

- Maximum Concurrency: Generate the highest possible number of independent tasks that can be executed simultaneously
- Forward Planning: Design Phase 1 tasks with awareness of downstream dependencies in later phases
- Interface-First Development: Define clear interfaces early to unblock dependent components
- Atomic Task Design: Break requirements into the smallest independently executable units
- Self-Contained Context: Provide sufficient context for autonomous execution

## Process Flow

1. Documentation Analysis
   - Parse STRUCTURE.md to identify all functionality requirements
   - Map current codebase structure and identify existing components
   - Create a gap analysis between current state and required functionality
   - Identify technical constraints and system boundaries
   - Extract all potential independent work units

2. Requirement Atomization
   - Break down requirements into atomic units (aim for 10+ concurrent tasks in Phase 1)
   - Identify shared interfaces and foundation components
   - Split complex features into independent micro-components
   - Extract cross-cutting concerns into separate tasks
   - Establish clear boundaries between different functional domains

3. Comprehensive Dependency Mapping
   - Create a detailed dependency graph showing relationships between components
   - Identify foundation components that enable maximum downstream development
   - Map all upstream and downstream dependencies
   - Prioritize components that unblock the most other tasks
   - Identify critical path components that require immediate attention

4. Interface-First Planning
   - Prioritize interface definitions in Phase 1 to enable parallel development of dependent components
   - Create mock implementations for interfaces to unblock dependent components
   - Define validation contracts between components
   - Establish data format and structure standards
   - Document API contracts for all component interactions

5. Query Generation Optimization
   - Generate at least 10 concurrent queries for Phase 1
   - Group queries into phases based on dependency chains
   - Optimize for balanced workload distribution
   - Ensure all critical path components are identified and prioritized
   - Include forward-looking context in Phase 1 queries to enable seamless integration in later phases

########## END REQUIREMENTS ##########

## Current Structure

### Components

- Component 1: Description of component 1
- Component 2: Description of component 2

### Interfaces

- Interface 1: Description of interface 1
- Interface 2: Description of interface 2

### Dependencies

- Dependency 1: Description of dependency 1
- Dependency 2: Description of dependency 2

## UI Mockups

### Screen 1

```
+------------------+
|    Header        |
+------------------+
|                  |
|    Content       |
|                  |
+------------------+
|    Footer        |
+------------------+
```

### Screen 2

```
+------------------+
|    Header        |
+------------------+
|    Sidebar  |    |
|            |     |
|            |     |
+------------+-----+
|    Footer        |
+------------------+
```
"""
        
    def identify_dependencies(self, tasks: List[AtomicTask]) -> DependencyGraph:
        """
        Identify dependencies between tasks and create a dependency graph
        
        Args:
            tasks: List of atomic tasks
            
        Returns:
            Dependency graph
        """
        graph = DependencyGraph(tasks)
        
        # Identify dependencies based on task descriptions and titles
        for task in tasks:
            for other_task in tasks:
                if task.id == other_task.id:
                    continue
                    
                # Check if other_task's title is mentioned in task's description
                if other_task.title.lower() in task.description.lower():
                    if other_task.id not in task.dependencies:
                        task.dependencies.append(other_task.id)
                        
        # Update the graph
        graph = DependencyGraph(tasks)
        
        return graph
        
    def prioritize_tasks(self, dependency_graph: DependencyGraph) -> List[List[AtomicTask]]:
        """
        Group tasks into phases based on dependencies, maximizing concurrency
        
        Args:
            dependency_graph: Dependency graph
            
        Returns:
            List of phases, each containing a list of tasks
        """
        # Get phases from the graph
        phase_ids = dependency_graph.get_phases()
        
        # Convert phase IDs to tasks
        phases = []
        for phase_id in phase_ids:
            phase_tasks = [dependency_graph.get_task(task_id) for task_id in phase_id]
            phases.append(phase_tasks)
            
        # Update task phases
        for i, phase in enumerate(phases):
            for task in phase:
                task.phase = i + 1
                
        return phases
        
    def generate_queries(self, tasks: List[AtomicTask], phase: int = 1) -> List[str]:
        """
        Generate optimized queries for a specific phase
        
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
            queries.append(query)
            
        return queries
        
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
        
    def update_requirements_with_tasks(self, tasks: List[AtomicTask]) -> None:
        """
        Update REQUIREMENTS.md with the given tasks
        
        Args:
            tasks: List of atomic tasks
        """
        if not self.requirements_path.exists():
            logger.warning(f"REQUIREMENTS.md not found at {self.requirements_path}")
            return
            
        with open(self.requirements_path, "r") as f:
            content = f.read()
            
        # Add a new section for atomic tasks
        content += "\n\n## Atomic Tasks\n\n"
        
        # Group tasks by phase
        tasks_by_phase = {}
        for task in tasks:
            if task.phase not in tasks_by_phase:
                tasks_by_phase[task.phase] = []
            tasks_by_phase[task.phase].append(task)
            
        # Add tasks by phase
        for phase in sorted(tasks_by_phase.keys()):
            content += f"\n### Phase {phase}\n\n"
            
            for task in tasks_by_phase[phase]:
                content += f"- {task.id}: {task.title}"
                if task.description:
                    content += f" - {task.description}"
                if task.dependencies:
                    content += f" (Dependencies: {', '.join(task.dependencies)})"
                content += "\n"
                
        with open(self.requirements_path, "w") as f:
            f.write(content)
            
        logger.info(f"Updated REQUIREMENTS.md with atomic tasks at {self.requirements_path}")
        
    def export_tasks_to_json(self, tasks: List[AtomicTask], output_path: str) -> None:
        """
        Export tasks to a JSON file
        
        Args:
            tasks: List of atomic tasks
            output_path: Path to the output file
        """
        data = [task.to_dict() for task in tasks]
        
        with open(output_path, "w") as f:
            json.dump(data, f, indent=2)
            
        logger.info(f"Exported tasks to {output_path}")
        
    def import_tasks_from_json(self, input_path: str) -> List[AtomicTask]:
        """
        Import tasks from a JSON file
        
        Args:
            input_path: Path to the input file
            
        Returns:
            List of atomic tasks
        """
        with open(input_path, "r") as f:
            data = json.load(f)
            
        tasks = [AtomicTask.from_dict(task_data) for task_data in data]
        
        logger.info(f"Imported tasks from {input_path}")
        
        return tasks
        
    def generate_interface_definitions(self, tasks: List[AtomicTask]) -> List[AtomicTask]:
        """
        Generate interface definitions for tasks
        
        Args:
            tasks: List of atomic tasks
            
        Returns:
            List of interface definition tasks
        """
        interface_tasks = []
        
        for task in tasks:
            # Check if task is likely to need an interface
            if any(keyword in task.title.lower() for keyword in ["api", "interface", "component", "service", "module"]):
                # Create an interface definition task
                interface_task = AtomicTask(
                    id=f"{task.id}-INTERFACE",
                    title=f"Interface for {task.title}",
                    description=f"Define the interface for {task.title}",
                    priority=task.priority + 1,  # Higher priority
                    dependencies=[],
                    phase=1,  # Always in phase 1
                    tags=task.tags + ["interface"],
                    estimated_time=30,  # 30 minutes
                    interface_definition=True,
                )
                
                # Add the interface task as a dependency of the original task
                task.dependencies.append(interface_task.id)
                
                interface_tasks.append(interface_task)
                
        return interface_tasks
        
    def create_mock_implementations(self, interface_tasks: List[AtomicTask]) -> List[AtomicTask]:
        """
        Create mock implementation tasks for interface definitions
        
        Args:
            interface_tasks: List of interface definition tasks
            
        Returns:
            List of mock implementation tasks
        """
        mock_tasks = []
        
        for task in interface_tasks:
            # Create a mock implementation task
            mock_task = AtomicTask(
                id=f"{task.id}-MOCK",
                title=f"Mock implementation for {task.title}",
                description=f"Create a mock implementation for {task.title}",
                priority=task.priority,
                dependencies=[task.id],
                phase=1,  # Always in phase 1
                tags=task.tags + ["mock"],
                estimated_time=60,  # 60 minutes
            )
            
            mock_tasks.append(mock_task)
            
        return mock_tasks
        
    def analyze_codebase(self, codebase_path: str) -> Dict[str, Any]:
        """
        Analyze the codebase to identify existing components
        
        Args:
            codebase_path: Path to the codebase
            
        Returns:
            Dictionary with analysis results
        """
        # This is a simplified implementation
        # A more sophisticated implementation would use static analysis tools
        
        analysis = {
            "components": [],
            "interfaces": [],
            "dependencies": [],
        }
        
        # Find Python files
        python_files = []
        for root, _, files in os.walk(codebase_path):
            for file in files:
                if file.endswith(".py"):
                    python_files.append(os.path.join(root, file))
                    
        # Analyze each file
        for file_path in python_files:
            with open(file_path, "r") as f:
                content = f.read()
                
            # Extract classes
            classes = re.findall(r'class\s+(\w+)', content)
            
            for class_name in classes:
                # Check if it's an interface
                if "Interface" in class_name or "Abstract" in class_name:
                    analysis["interfaces"].append({
                        "name": class_name,
                        "file": file_path,
                    })
                else:
                    analysis["components"].append({
                        "name": class_name,
                        "file": file_path,
                    })
                    
            # Extract imports
            imports = re.findall(r'import\s+(.*?)$|from\s+(.*?)\s+import', content, re.MULTILINE)
            
            for import_match in imports:
                import_name = import_match[0] or import_match[1]
                if import_name:
                    analysis["dependencies"].append({
                        "from": os.path.basename(file_path),
                        "to": import_name,
                    })
                    
        return analysis
        
    def create_gap_analysis(self, requirements: List[AtomicTask], codebase_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a gap analysis between requirements and existing codebase
        
        Args:
            requirements: List of atomic tasks
            codebase_analysis: Codebase analysis results
            
        Returns:
            Dictionary with gap analysis results
        """
        gap_analysis = {
            "missing_components": [],
            "missing_interfaces": [],
            "existing_components": [],
        }
        
        # Extract component names from requirements
        required_components = set()
        for task in requirements:
            # Extract potential component names from task title and description
            words = re.findall(r'\b[A-Z][a-z]+(?:[A-Z][a-z]+)*\b', task.title + " " + task.description)
            required_components.update(words)
            
        # Check which components already exist
        existing_component_names = {component["name"] for component in codebase_analysis["components"]}
        existing_interface_names = {interface["name"] for interface in codebase_analysis["interfaces"]}
        
        for component in required_components:
            if component in existing_component_names:
                gap_analysis["existing_components"].append(component)
            else:
                gap_analysis["missing_components"].append(component)
                
            # Check if interface exists
            interface_name = f"{component}Interface"
            if interface_name not in existing_interface_names:
                gap_analysis["missing_interfaces"].append(interface_name)
                
        return gap_analysis
        
    def generate_validation_contracts(self, interface_tasks: List[AtomicTask]) -> List[AtomicTask]:
        """
        Generate validation contract tasks for interface definitions
        
        Args:
            interface_tasks: List of interface definition tasks
            
        Returns:
            List of validation contract tasks
        """
        validation_tasks = []
        
        for task in interface_tasks:
            # Create a validation contract task
            validation_task = AtomicTask(
                id=f"{task.id}-VALIDATION",
                title=f"Validation contract for {task.title}",
                description=f"Define validation rules and contracts for {task.title}",
                priority=task.priority,
                dependencies=[task.id],
                phase=1,  # Always in phase 1
                tags=task.tags + ["validation"],
                estimated_time=45,  # 45 minutes
            )
            
            validation_tasks.append(validation_task)
            
        return validation_tasks
        
    def generate_data_format_standards(self, interface_tasks: List[AtomicTask]) -> List[AtomicTask]:
        """
        Generate data format standard tasks for interface definitions
        
        Args:
            interface_tasks: List of interface definition tasks
            
        Returns:
            List of data format standard tasks
        """
        format_tasks = []
        
        for task in interface_tasks:
            # Create a data format standard task
            format_task = AtomicTask(
                id=f"{task.id}-FORMAT",
                title=f"Data format standards for {task.title}",
                description=f"Define data format and structure standards for {task.title}",
                priority=task.priority,
                dependencies=[task.id],
                phase=1,  # Always in phase 1
                tags=task.tags + ["format"],
                estimated_time=30,  # 30 minutes
            )
            
            format_tasks.append(format_task)
            
        return format_tasks
        
    def generate_api_contracts(self, interface_tasks: List[AtomicTask]) -> List[AtomicTask]:
        """
        Generate API contract tasks for interface definitions
        
        Args:
            interface_tasks: List of interface definition tasks
            
        Returns:
            List of API contract tasks
        """
        contract_tasks = []
        
        for task in interface_tasks:
            # Create an API contract task
            contract_task = AtomicTask(
                id=f"{task.id}-CONTRACT",
                title=f"API contract for {task.title}",
                description=f"Document API contracts for {task.title}",
                priority=task.priority,
                dependencies=[task.id],
                phase=1,  # Always in phase 1
                tags=task.tags + ["contract"],
                estimated_time=60,  # 60 minutes
            )
            
            contract_tasks.append(contract_task)
            
        return contract_tasks
        
    def get_atomic_tasks(self) -> List[AtomicTask]:
        """
        Get atomic tasks
        
        Returns:
            List of atomic tasks
        """
        return self.atomic_tasks
        
    def get_atomic_tasks_dict(self) -> List[Dict[str, Any]]:
        """
        Get atomic tasks as a list of dictionaries
        
        Returns:
            List of atomic tasks as dictionaries
        """
        return [task.to_dict() for task in self.atomic_tasks]
        
    def get_dependency_graph_dict(self) -> Dict[str, Any]:
        """
        Get dependency graph as a dictionary
        
        Returns:
            Dependency graph as a dictionary
        """
        if self.dependency_graph:
            return self.dependency_graph.to_dict()
        return {"tasks": [], "graph": {}}
    
    def initialize(self) -> None:
        """
        Initialize the requirements manager
        """
        # Create requirements file if it doesn't exist
        if not os.path.exists(self.requirements_path):
            self.create_requirements_file()
            
        # Parse requirements
        self.atomic_tasks = self.parse_requirements()
        
        # Create dependency graph
        if self.atomic_tasks:
            self.dependency_graph = self.identify_dependencies(self.atomic_tasks)
        else:
            self.dependency_graph = DependencyGraph()
            
        logger.info("Requirements manager initialized")
