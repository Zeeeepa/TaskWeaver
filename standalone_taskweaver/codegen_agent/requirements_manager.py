#!/usr/bin/env python3
"""
Requirements Manager for TaskWeaver and Codegen Integration

This module provides functionality for creating, parsing, and managing
requirements documents (REQUIREMENTS.md) for projects. It supports breaking
down requirements into atomic tasks for concurrent execution.
"""

import os
import sys
import json
import logging
import re
from typing import Dict, List, Optional, Any, Union, Tuple, Set
from pathlib import Path
import networkx as nx

from injector import inject

from standalone_taskweaver.app.app import TaskWeaverApp
from standalone_taskweaver.config.config_mgt import AppConfigSource
from standalone_taskweaver.logging import TelemetryLogger
from standalone_taskweaver.codegen_agent.integration import CodegenIntegration

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("requirements-manager")

class RequirementsManager:
    """
    Manager for creating, parsing, and managing requirements documents
    """
    
    @inject
    def __init__(
        self,
        app: TaskWeaverApp,
        config: AppConfigSource,
        logger: TelemetryLogger,
        codegen_integration: CodegenIntegration,
    ) -> None:
        self.app = app
        self.config = config
        self.logger = logger
        self.codegen_integration = codegen_integration
        
    def create_requirements_document(self, 
                                    project_name: str, 
                                    requirements: str, 
                                    current_structure: Optional[str] = None,
                                    ui_mockup: Optional[str] = None) -> Tuple[bool, Optional[str]]:
        """
        Create or update a REQUIREMENTS.md file in the repository
        
        Args:
            project_name: Name of the project
            requirements: Requirements content
            current_structure: Current project structure (optional)
            ui_mockup: UI mockup content (optional)
            
        Returns:
            Tuple[bool, Optional[str]]: (Success status, Error message if any)
        """
        try:
            # Format the requirements document
            content = self._format_requirements_document(
                project_name=project_name,
                requirements=requirements,
                current_structure=current_structure,
                ui_mockup=ui_mockup
            )
            
            # Use the CodegenIntegration to create or update the document
            success, error = self.codegen_integration.create_requirements_document(content)
            
            if success:
                self.logger.info("Requirements document created successfully")
            else:
                self.logger.error(f"Error creating requirements document: {error}")
                
            return success, error
        except Exception as e:
            error_msg = f"Error creating requirements document: {str(e)}"
            self.logger.error(error_msg)
            return False, error_msg
            
    def _format_requirements_document(self, 
                                     project_name: str, 
                                     requirements: str,
                                     current_structure: Optional[str] = None,
                                     ui_mockup: Optional[str] = None) -> str:
        """
        Format the requirements document
        
        Args:
            project_name: Name of the project
            requirements: Requirements content
            current_structure: Current project structure (optional)
            ui_mockup: UI mockup content (optional)
            
        Returns:
            str: Formatted requirements document
        """
        # Create the document header
        header = f"# {project_name} Requirements\n\n"
        
        # Add timestamp
        from datetime import datetime
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        header += f"*Last updated: {timestamp}*\n\n"
        
        # Add requirements section
        requirements_section = "## REQUIREMENTS\n\n"
        requirements_section += requirements + "\n\n"
        
        # Add current structure section if provided
        structure_section = ""
        if current_structure:
            structure_section = "## CURRENT STRUCTURE\n\n"
            structure_section += current_structure + "\n\n"
        
        # Add UI mockup section if provided
        ui_section = ""
        if ui_mockup:
            ui_section = "## UI MOCKUP\n\n"
            ui_section += ui_mockup + "\n\n"
        
        # Combine all sections
        document = header + requirements_section + structure_section + ui_section
        
        return document
        
    def parse_requirements_document(self, document_content: str) -> Dict[str, Any]:
        """
        Parse a requirements document
        
        Args:
            document_content: Content of the requirements document
            
        Returns:
            Dict[str, Any]: Parsed requirements
        """
        try:
            # Validate input
            if not document_content or not isinstance(document_content, str):
                self.logger.error("Invalid document content: empty or not a string")
                return self._create_empty_requirements_result()
                
            # Check if document has required sections
            if "## REQUIREMENTS" not in document_content:
                self.logger.error("Invalid document content: missing REQUIREMENTS section")
                return self._create_empty_requirements_result()
            
            # Parse the document into sections
            sections = self._parse_document_sections(document_content)
            
            # Extract requirements
            requirements = sections.get("REQUIREMENTS", "")
            if not requirements:
                self.logger.error("Requirements section is empty")
                return self._create_empty_requirements_result()
            
            # Extract current structure
            current_structure = sections.get("CURRENT STRUCTURE", "")
            
            # Extract UI mockup
            ui_mockup = sections.get("UI MOCKUP", "")
            
            # Parse requirements into atomic tasks
            atomic_tasks = self._parse_requirements_into_tasks(requirements)
            
            if not atomic_tasks:
                self.logger.warning("No atomic tasks found in requirements")
            
            # Create dependency graph
            dependency_graph = self._create_dependency_graph(atomic_tasks)
            
            # Group tasks into phases
            phases = self._group_tasks_into_phases(dependency_graph)
            
            return {
                "requirements": requirements,
                "current_structure": current_structure,
                "ui_mockup": ui_mockup,
                "atomic_tasks": atomic_tasks,
                "dependency_graph": dependency_graph,
                "phases": phases
            }
        except Exception as e:
            self.logger.error(f"Error parsing requirements document: {str(e)}")
            return self._create_empty_requirements_result()
            
    def _create_empty_requirements_result(self) -> Dict[str, Any]:
        """
        Create an empty requirements result
        
        Returns:
            Dict[str, Any]: Empty requirements result
        """
        return {
            "requirements": "",
            "current_structure": "",
            "ui_mockup": "",
            "atomic_tasks": [],
            "dependency_graph": {},
            "phases": []
        }
        
    def _parse_document_sections(self, document_content: str) -> Dict[str, str]:
        """
        Parse a document into sections
        
        Args:
            document_content: Content of the document
            
        Returns:
            Dict[str, str]: Sections of the document
        """
        sections = {}
        
        # Define a pattern to match section headers
        section_pattern = r"##\s+([A-Z\s]+)\n\n(.*?)(?=##\s+[A-Z\s]+\n\n|$)"
        
        # Find all sections
        matches = re.finditer(section_pattern, document_content, re.DOTALL)
        
        for match in matches:
            section_name = match.group(1).strip()
            section_content = match.group(2).strip()
            sections[section_name] = section_content
            
        return sections
        
    def _parse_requirements_into_tasks(self, requirements: str) -> List[Dict[str, Any]]:
        """
        Parse requirements into atomic tasks
        
        Args:
            requirements: Requirements content
            
        Returns:
            List[Dict[str, Any]]: List of atomic tasks
        """
        atomic_tasks = []
        
        # Split requirements into paragraphs
        paragraphs = requirements.split("\n\n")
        
        for i, paragraph in enumerate(paragraphs):
            # Skip empty paragraphs
            if not paragraph.strip():
                continue
                
            # Create a task for each paragraph
            task = {
                "id": f"task-{i+1}",
                "description": paragraph.strip(),
                "dependencies": [],
                "type": self._determine_task_type(paragraph),
                "priority": self._determine_task_priority(paragraph),
                "estimated_effort": self._estimate_task_effort(paragraph)
            }
            
            atomic_tasks.append(task)
            
        # Identify dependencies between tasks
        for i, task in enumerate(atomic_tasks):
            dependencies = self._identify_task_dependencies(task, atomic_tasks[:i])
            task["dependencies"] = dependencies
            
        return atomic_tasks
        
    def _determine_task_type(self, task_description: str) -> str:
        """
        Determine the type of a task
        
        Args:
            task_description: Description of the task
            
        Returns:
            str: Type of the task
        """
        # Keywords for different task types
        interface_keywords = ["interface", "api", "contract", "protocol", "definition"]
        foundation_keywords = ["foundation", "core", "base", "infrastructure", "framework"]
        utility_keywords = ["utility", "helper", "common", "shared", "service"]
        feature_keywords = ["feature", "functionality", "capability", "user story"]
        ui_keywords = ["ui", "user interface", "frontend", "display", "view"]
        
        # Check for keywords in the task description
        description_lower = task_description.lower()
        
        if any(keyword in description_lower for keyword in interface_keywords):
            return "interface"
        elif any(keyword in description_lower for keyword in foundation_keywords):
            return "foundation"
        elif any(keyword in description_lower for keyword in utility_keywords):
            return "utility"
        elif any(keyword in description_lower for keyword in ui_keywords):
            return "ui"
        elif any(keyword in description_lower for keyword in feature_keywords):
            return "feature"
        else:
            return "other"
            
    def _determine_task_priority(self, task_description: str) -> int:
        """
        Determine the priority of a task
        
        Args:
            task_description: Description of the task
            
        Returns:
            int: Priority of the task (1-5, where 1 is highest)
        """
        # Keywords for different priority levels
        high_priority_keywords = ["critical", "essential", "highest", "urgent", "must"]
        medium_priority_keywords = ["important", "should", "significant"]
        low_priority_keywords = ["nice to have", "optional", "could", "may"]
        
        # Check for keywords in the task description
        description_lower = task_description.lower()
        
        if any(keyword in description_lower for keyword in high_priority_keywords):
            return 1
        elif any(keyword in description_lower for keyword in medium_priority_keywords):
            return 3
        elif any(keyword in description_lower for keyword in low_priority_keywords):
            return 5
        else:
            return 3  # Default to medium priority
            
    def _estimate_task_effort(self, task_description: str) -> int:
        """
        Estimate the effort required for a task
        
        Args:
            task_description: Description of the task
            
        Returns:
            int: Estimated effort (1-5, where 1 is lowest)
        """
        # Simple heuristic based on description length
        word_count = len(task_description.split())
        
        if word_count < 20:
            return 1
        elif word_count < 50:
            return 2
        elif word_count < 100:
            return 3
        elif word_count < 200:
            return 4
        else:
            return 5
            
    def _identify_task_dependencies(self, task: Dict[str, Any], previous_tasks: List[Dict[str, Any]]) -> List[str]:
        """
        Identify dependencies between tasks
        
        Args:
            task: Current task
            previous_tasks: List of previous tasks
            
        Returns:
            List[str]: List of task IDs that this task depends on
        """
        dependencies = []
        
        # Check for explicit dependencies in the task description
        description_lower = task["description"].lower()
        
        # Check for dependencies based on task type
        if task["type"] == "feature":
            # Features may depend on interfaces and foundation components
            for prev_task in previous_tasks:
                if prev_task["type"] in ["interface", "foundation"]:
                    dependencies.append(prev_task["id"])
        elif task["type"] == "ui":
            # UI components may depend on features and interfaces
            for prev_task in previous_tasks:
                if prev_task["type"] in ["feature", "interface"]:
                    dependencies.append(prev_task["id"])
                    
        # Remove duplicates
        dependencies = list(set(dependencies))
        
        return dependencies
        
    def _create_dependency_graph(self, tasks: List[Dict[str, Any]]) -> Dict[str, List[str]]:
        """
        Create a dependency graph for tasks
        
        Args:
            tasks: List of tasks
            
        Returns:
            Dict[str, List[str]]: Dependency graph
        """
        dependency_graph = {}
        
        for task in tasks:
            dependency_graph[task["id"]] = task["dependencies"]
            
        return dependency_graph
        
    def _group_tasks_into_phases(self, dependency_graph: Dict[str, List[str]]) -> List[List[str]]:
        """
        Group tasks into phases based on dependencies
        
        Args:
            dependency_graph: Dependency graph
            
        Returns:
            List[List[str]]: List of phases, where each phase is a list of task IDs
        """
        # Create a directed graph
        G = nx.DiGraph()
        
        # Add all nodes first
        for task_id in dependency_graph.keys():
            G.add_node(task_id)
        
        # Add edges after ensuring nodes exist
        for task_id, dependencies in dependency_graph.items():
            for dep in dependencies:
                if dep in dependency_graph:
                    G.add_edge(dep, task_id)
                else:
                    self.logger.warning(f"Task {task_id} references non-existent dependency {dep}")
                
        # Compute the topological sort
        try:
            topological_sort = list(nx.topological_sort(G))
        except nx.NetworkXUnfeasible:
            # Handle cycles in the graph
            self.logger.warning("Dependency graph contains cycles. Using approximate topological sort.")
            topological_sort = list(G.nodes())
            
        # Group tasks into phases
        phases = []
        remaining_tasks = set(topological_sort)
        
        while remaining_tasks:
            # Find tasks with no remaining dependencies
            current_phase = []
            for task_id in list(remaining_tasks):
                dependencies = [dep for dep in dependency_graph.get(task_id, []) if dep in dependency_graph]
                if all(dep not in remaining_tasks for dep in dependencies):
                    current_phase.append(task_id)
                    
            # If no tasks were found, there might be a cycle
            if not current_phase:
                # Detect cycle in dependency graph
                self.logger.warning("Detected cycle in dependency graph. Breaking cycle.")
                # Find task with fewest dependencies to minimize impact
                min_deps = float('inf')
                task_to_break = None
                
                for task_id in remaining_tasks:
                    deps_in_remaining = sum(1 for dep in dependency_graph.get(task_id, []) 
                                          if dep in remaining_tasks)
                    if deps_in_remaining < min_deps:
                        min_deps = deps_in_remaining
                        task_to_break = task_id
                
                if task_to_break:
                    current_phase.append(task_to_break)
                else:
                    # Fallback: take the first remaining task
                    task_id = next(iter(remaining_tasks))
                    current_phase.append(task_id)
                    
            # Remove tasks in the current phase from remaining tasks
            remaining_tasks -= set(current_phase)
            
            # Add the current phase to the list of phases
            phases.append(current_phase)
            
        return phases
        
    def generate_concurrent_queries(self, parsed_requirements: Dict[str, Any], phase: int = 1) -> List[str]:
        """
        Generate concurrent queries for a specific phase
        
        Args:
            parsed_requirements: Parsed requirements
            phase: Phase number (1-based)
            
        Returns:
            List[str]: List of queries
        """
        try:
            # Get tasks for the specified phase
            phases = parsed_requirements.get("phases", [])
            
            if phase > len(phases):
                self.logger.error(f"Phase {phase} does not exist")
                return []
                
            phase_tasks = phases[phase - 1]
            
            # Get task details
            all_tasks = parsed_requirements.get("atomic_tasks", [])
            task_map = {task["id"]: task for task in all_tasks}
            
            # Generate queries for each task
            queries = []
            for task_id in phase_tasks:
                task = task_map.get(task_id)
                if task:
                    query = self._generate_query_for_task(task, parsed_requirements)
                    queries.append(query)
                    
            return queries
        except Exception as e:
            self.logger.error(f"Error generating concurrent queries: {str(e)}")
            return []
            
    def _generate_query_for_task(self, task: Dict[str, Any], parsed_requirements: Dict[str, Any]) -> str:
        """
        Generate a query for a task
        
        Args:
            task: Task details
            parsed_requirements: Parsed requirements
            
        Returns:
            str: Query for the task
        """
        # Get task details
        task_id = task["id"]
        description = task["description"]
        task_type = task["type"]
        
        # Get dependency information
        dependencies = task.get("dependencies", [])
        all_tasks = parsed_requirements.get("atomic_tasks", [])
        task_map = {task["id"]: task for task in all_tasks}
        
        dependency_descriptions = []
        for dep_id in dependencies:
            dep_task = task_map.get(dep_id)
            if dep_task:
                dependency_descriptions.append(f"- {dep_task['description']}")
                
        dependency_section = ""
        if dependency_descriptions:
            dependency_section = "## Dependencies\n\n" + "\n".join(dependency_descriptions) + "\n\n"
            
        # Get current structure
        current_structure = parsed_requirements.get("current_structure", "")
        structure_section = ""
        if current_structure:
            structure_section = "## Current Structure\n\n" + current_structure + "\n\n"
            
        # Create the query
        query = f"""# Task: {task_id}

## Description
{description}

## Task Type
{task_type}

{dependency_section}
{structure_section}
## Implementation Guidelines
- Follow the interface-first development approach
- Ensure the implementation is modular and reusable
- Write comprehensive tests
- Document the implementation
- Consider future extensibility

Please implement this task according to the requirements and guidelines.
"""
        
        return query

class AtomicTask:
    """
    Represents an atomic task that can be executed independently
    """
    
    def __init__(
        self,
        task_id: str,
        description: str,
        dependencies: List[str] = None,
        task_type: str = "other",
        priority: int = 3,
        estimated_effort: int = 3
    ) -> None:
        self.id = task_id
        self.description = description
        self.dependencies = dependencies or []
        self.type = task_type
        self.priority = priority
        self.estimated_effort = estimated_effort
        
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert the task to a dictionary
        
        Returns:
            Dict[str, Any]: Dictionary representation of the task
        """
        return {
            "id": self.id,
            "description": self.description,
            "dependencies": self.dependencies,
            "type": self.type,
            "priority": self.priority,
            "estimated_effort": self.estimated_effort
        }
        
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'AtomicTask':
        """
        Create a task from a dictionary
        
        Args:
            data: Dictionary representation of the task
            
        Returns:
            AtomicTask: Task object
        """
        return cls(
            task_id=data["id"],
            description=data["description"],
            dependencies=data.get("dependencies", []),
            task_type=data.get("type", "other"),
            priority=data.get("priority", 3),
            estimated_effort=data.get("estimated_effort", 3)
        )

class DependencyGraph:
    """
    Represents a dependency graph for tasks
    """
    
    def __init__(self) -> None:
        self.graph = nx.DiGraph()
        
    def add_task(self, task: AtomicTask) -> None:
        """
        Add a task to the graph
        
        Args:
            task: Task to add
        """
        self.graph.add_node(task.id, task=task)
        
    def add_dependency(self, task_id: str, dependency_id: str) -> None:
        """
        Add a dependency between tasks
        
        Args:
            task_id: ID of the dependent task
            dependency_id: ID of the task that is depended on
        """
        self.graph.add_edge(dependency_id, task_id)
        
    def get_dependencies(self, task_id: str) -> List[str]:
        """
        Get the dependencies of a task
        
        Args:
            task_id: ID of the task
            
        Returns:
            List[str]: List of task IDs that this task depends on
        """
        return list(self.graph.predecessors(task_id))
        
    def get_dependents(self, task_id: str) -> List[str]:
        """
        Get the tasks that depend on this task
        
        Args:
            task_id: ID of the task
            
        Returns:
            List[str]: List of task IDs that depend on this task
        """
        return list(self.graph.successors(task_id))
        
    def get_all_tasks(self) -> List[str]:
        """
        Get all tasks in the graph
        
        Returns:
            List[str]: List of all task IDs
        """
        return list(self.graph.nodes())
        
    def get_task(self, task_id: str) -> Optional[AtomicTask]:
        """
        Get a task by ID
        
        Args:
            task_id: ID of the task
            
        Returns:
            Optional[AtomicTask]: Task object if found, None otherwise
        """
        if task_id in self.graph:
            return self.graph.nodes[task_id]["task"]
        return None
        
    def group_tasks_into_phases(self) -> List[List[str]]:
        """
        Group tasks into phases based on dependencies
        
        Returns:
            List[List[str]]: List of phases, where each phase is a list of task IDs
        """
        # Compute the topological sort
        try:
            topological_sort = list(nx.topological_sort(self.graph))
        except nx.NetworkXUnfeasible:
            # Handle cycles in the graph
            logger.warning("Dependency graph contains cycles. Using approximate topological sort.")
            topological_sort = list(self.graph.nodes())
            
        # Group tasks into phases
        phases = []
        remaining_tasks = set(topological_sort)
        
        while remaining_tasks:
            # Find tasks with no remaining dependencies
            current_phase = []
            for task_id in list(remaining_tasks):
                dependencies = self.get_dependencies(task_id)
                if all(dep not in remaining_tasks for dep in dependencies):
                    current_phase.append(task_id)
                    
            # If no tasks were found, there might be a cycle
            if not current_phase:
                # Detect cycle in dependency graph
                self.logger.warning("Detected cycle in dependency graph. Breaking cycle.")
                # Find task with fewest dependencies to minimize impact
                min_deps = float('inf')
                task_to_break = None
                
                for task_id in remaining_tasks:
                    deps_in_remaining = sum(1 for dep in dependency_graph.get(task_id, []) 
                                          if dep in remaining_tasks)
                    if deps_in_remaining < min_deps:
                        min_deps = deps_in_remaining
                        task_to_break = task_id
                
                if task_to_break:
                    current_phase.append(task_to_break)
                else:
                    # Fallback: take the first remaining task
                    task_id = next(iter(remaining_tasks))
                    current_phase.append(task_id)
                    
            # Remove tasks in the current phase from remaining tasks
            remaining_tasks -= set(current_phase)
            
            # Add the current phase to the list of phases
            phases.append(current_phase)
            
        return phases
        
    def to_dict(self) -> Dict[str, List[str]]:
        """
        Convert the graph to a dictionary
        
        Returns:
            Dict[str, List[str]]: Dictionary representation of the graph
        """
        graph_dict = {}
        for task_id in self.graph.nodes():
            graph_dict[task_id] = list(self.graph.predecessors(task_id))
            
        return graph_dict
        
    @classmethod
    def from_dict(cls, data: Dict[str, List[str]]) -> 'DependencyGraph':
        """
        Create a graph from a dictionary
        
        Args:
            data: Dictionary representation of the graph
            
        Returns:
            DependencyGraph: Graph object
        """
        graph = cls()
        
        # Add nodes
        for task_id in data:
            graph.graph.add_node(task_id)
            
        # Add edges
        for task_id, dependencies in data.items():
            for dep in dependencies:
                graph.graph.add_edge(dep, task_id)
                
        return graph

    def _visualize_dependency_graph(self, dependency_graph: Dict[str, List[str]]) -> str:
        """
        Visualize a dependency graph
        
        Args:
            dependency_graph: Dependency graph
            
        Returns:
            str: Visualization of the graph
        """
        try:
            import networkx as nx
            import matplotlib.pyplot as plt
            from io import BytesIO
            import base64
            
            # Create a directed graph
            G = nx.DiGraph()
            
            # Add all nodes first
            for task_id in dependency_graph.keys():
                G.add_node(task_id)
            
            # Add edges after ensuring nodes exist
            for task_id, dependencies in dependency_graph.items():
                for dep in dependencies:
                    if dep in dependency_graph:
                        G.add_edge(dep, task_id)
                    else:
                        self.logger.warning(f"Task {task_id} references non-existent dependency {dep}")
            
            # Draw the graph
            pos = nx.spring_layout(G)
            nx.draw(G, pos, with_labels=True, node_color='lightblue', node_size=1500, font_size=10)
            plt.axis('off')
            plt.tight_layout()
            
            # Save the graph as an image
            img = BytesIO()
            plt.savefig(img, format='png')
            img.seek(0)
            img_base64 = base64.b64encode(img.getvalue()).decode('utf-8')
            
            return img_base64
        except Exception as e:
            self.logger.error(f"Error visualizing dependency graph: {str(e)}")
            return None
