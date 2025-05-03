# TaskWeaver-Codegen Concurrent Feature Deployment

This module enhances the TaskWeaver-Codegen integration with support for concurrent feature deployment, following the principles of maximum concurrency, forward planning, interface-first development, atomic task design, and self-contained context.

## Overview

The enhanced integration consists of the following components:

1. **Requirements Manager**: Creates and parses REQUIREMENTS.md and STRUCTURE.md files, breaks down requirements into atomic tasks, identifies dependencies, and prioritizes tasks for concurrent execution.

2. **Concurrent Execution Engine**: Executes multiple Codegen tasks concurrently, monitors their progress, and handles errors with robust fallback mechanisms.

3. **Interface Generator**: Generates interfaces for components to enable parallel development, creates mock implementations, validation contracts, data format standards, and API contracts.

4. **Concurrent Context Manager**: Maintains isolated contexts for different tasks and supports merging contexts.

5. **Query Generation Framework**: Generates optimized queries for concurrent execution, balances workload, identifies critical paths, and adds forward-looking context.

## Features

- Create and parse REQUIREMENTS.md and STRUCTURE.md files
- Break down requirements into atomic tasks
- Identify dependencies between tasks
- Group tasks into phases for concurrent execution
- Execute tasks concurrently with the Codegen API
- Generate interfaces for components
- Create mock implementations for interfaces
- Handle errors with robust fallback mechanisms
- Maintain isolated contexts for different tasks
- Generate optimized queries for concurrent execution
- Balance workload across tasks
- Identify critical paths through the dependency graph
- Add forward-looking context to queries

## Installation

Ensure you have TaskWeaver installed, then install the required dependencies:

```bash
pip install codegen
```

## Usage

### Command-Line Interface

The module provides a command-line interface for common operations:

```bash
# Create a REQUIREMENTS.md file
python -m standalone_taskweaver.codegen_agent.cli create-requirements

# Create a STRUCTURE.md file
python -m standalone_taskweaver.codegen_agent.cli create-structure

# Parse REQUIREMENTS.md into atomic tasks
python -m standalone_taskweaver.codegen_agent.cli parse-requirements

# Identify dependencies between tasks
python -m standalone_taskweaver.codegen_agent.cli identify-dependencies

# Group tasks into phases
python -m standalone_taskweaver.codegen_agent.cli prioritize-tasks

# Generate queries for a specific phase
python -m standalone_taskweaver.codegen_agent.cli generate-queries --phase 1

# Execute queries using the Codegen API
python -m standalone_taskweaver.codegen_agent.cli execute-queries --input-file queries.json --org-id YOUR_ORG_ID --token YOUR_TOKEN

# Generate interface for a component
python -m standalone_taskweaver.codegen_agent.cli generate-interface --name UserService --description "User authentication service" --org-id YOUR_ORG_ID --token YOUR_TOKEN

# Create mock implementation for an interface
python -m standalone_taskweaver.codegen_agent.cli create-mock --input-file interface.txt --org-id YOUR_ORG_ID --token YOUR_TOKEN

# Execute tasks concurrently
python -m standalone_taskweaver.codegen_agent.cli execute-tasks --input-file tasks.json --org-id YOUR_ORG_ID --token YOUR_TOKEN
```

### Programmatic Usage

You can also use the module programmatically:

```python
from standalone_taskweaver.codegen_agent.integration import CodegenIntegration
from standalone_taskweaver.codegen_agent.requirements_manager import AtomicTask

# Initialize the integration
integration = CodegenIntegration(app, config, logger)
integration.initialize(
    github_token="your_github_token",
    codegen_token="your_codegen_token",
    ngrok_token="your_ngrok_token",
    codegen_org_id="your_codegen_org_id",
    repo_name="your_repo_name"
)

# Create a REQUIREMENTS.md file
integration.create_requirements_file()

# Parse REQUIREMENTS.md into atomic tasks
tasks = integration.parse_requirements()

# Identify dependencies between tasks
graph = integration.identify_dependencies(tasks)

# Group tasks into phases
phases = integration.prioritize_tasks(graph)

# Generate queries for a specific phase
queries = integration.generate_queries_from_tasks(tasks, phase=1)

# Execute queries concurrently
results = integration.execute_queries_concurrently(queries)

# Generate interface for a component
component_spec = {
    "name": "UserService",
    "description": "User authentication service",
}
interface = integration.generate_interface(component_spec)

# Create mock implementation for an interface
mock = integration.create_mock_implementation(interface)

# Execute tasks concurrently
import asyncio
task_results = asyncio.run(integration.execute_tasks(tasks))
```

## Example

See the `examples/concurrent_execution_example.py` file for a complete example of concurrent execution.

## Process Flow

1. **Documentation Analysis**
   - Parse STRUCTURE.md to identify all functionality requirements
   - Map current codebase structure and identify existing components
   - Create a gap analysis between current state and required functionality
   - Identify technical constraints and system boundaries
   - Extract all potential independent work units

2. **Requirement Atomization**
   - Break down requirements into atomic units (aim for 10+ concurrent tasks in Phase 1)
   - Identify shared interfaces and foundation components
   - Split complex features into independent micro-components
   - Extract cross-cutting concerns into separate tasks
   - Establish clear boundaries between different functional domains

3. **Comprehensive Dependency Mapping**
   - Create a detailed dependency graph showing relationships between components
   - Identify foundation components that enable maximum downstream development
   - Map all upstream and downstream dependencies
   - Prioritize components that unblock the most other tasks
   - Identify critical path components that require immediate attention

4. **Interface-First Planning**
   - Prioritize interface definitions in Phase 1 to enable parallel development of dependent components
   - Create mock implementations for interfaces to unblock dependent components
   - Define validation contracts between components
   - Establish data format and structure standards
   - Document API contracts for all component interactions

5. **Query Generation Optimization**
   - Generate at least 10 concurrent queries for Phase 1
   - Group queries into phases based on dependency chains
   - Optimize for balanced workload distribution
   - Ensure all critical path components are identified and prioritized
   - Include forward-looking context in Phase 1 queries to enable seamless integration in later phases

## Phase Planning Strategy

### Phase 1: Foundation Components

- Focus on components with no dependencies that enable downstream development
- Prioritize interface definitions and core functionality
- Include shared utilities and common services
- Establish patterns and standards for later phases
- Create mock implementations for interfaces

### Subsequent Phases

- Build upon completed Phase 1 components
- Integrate foundation components into higher-level features
- Implement business logic dependent on foundation components
- Focus on user-facing features and integration points
- Include validation and verification components

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

