# Codegen Agent with Concurrent Execution

This directory contains the Codegen agent implementation for TaskWeaver with support for concurrent execution of tasks.

## Overview

The Codegen agent provides a comprehensive implementation of the Codegen agent that supports multithreaded requests to the Codegen API while referencing project requirements and context. It allows for concurrent execution of tasks, making it ideal for executing deployment steps in parallel.

## Components

- `codegen_agent.py`: Main Codegen agent implementation
- `concurrent_execution.py`: Concurrent execution engine for executing tasks in parallel
- `concurrent_context_manager.py`: Context manager for managing context in concurrent execution
- `weaver_integration.py`: Integration between TaskWeaver's weaver component and the Codegen agent
- `requirements_manager.py`: Manager for parsing requirements and creating atomic tasks
- `bidirectional_context.py`: Bidirectional context manager for sharing context between TaskWeaver and Codegen
- `planner_integration.py`: Integration between TaskWeaver's planner and Codegen
- `integration.py`: Integration between Codegen and TaskWeaver
- `interface_generator.py`: Generator for interfaces and mock implementations
- `query_generation.py`: Framework for generating optimized queries
- `advanced_api.py`: Advanced API for Codegen

## Usage

### Basic Usage

```python
from standalone_taskweaver.codegen_agent.codegen_agent import CodegenAgent

# Create a CodegenAgent instance
agent = CodegenAgent(app, config, logger)

# Initialize the agent with a Codegen token
agent.initialize("your-codegen-token")

# Set the project context
agent.set_project_context(
    project_name="My Project",
    project_description="A sample project",
    requirements_text="This project requires..."
)

# Execute tasks
results = agent.execute_tasks(max_concurrent_tasks=3)

# Get the status of a task
status = agent.get_task_status("task-id")

# Get the result of a task
result = agent.get_task_result("task-id")

# Get all task results
all_results = agent.get_all_task_results()

# Get the status of the agent
status = agent.get_status()

# Cancel all running tasks
agent.cancel_all_tasks()
```

### Weaver Integration

```python
from standalone_taskweaver.codegen_agent.weaver_integration import CodegenWeaverIntegration

# Create a CodegenWeaverIntegration instance
integration = CodegenWeaverIntegration(app, config, logger)

# Initialize the integration with a Codegen token
integration.initialize("your-codegen-token")

# Set the project context
integration.set_project_context(
    project_name="My Project",
    project_description="A sample project",
    requirements_text="This project requires..."
)

# Parse deployment steps
steps = integration.parse_deployment_steps("""
Step 1: Initialize the project
Create a new directory and initialize a Git repository.

Step 2: Install dependencies
Install the required dependencies using npm.
""")

# Execute deployment steps
results = integration.execute_deployment_steps(max_concurrent_steps=2)

# Get the status of a deployment step
status = integration.get_step_status("step-1")

# Get the result of a deployment step
result = integration.get_step_result("step-1")

# Get all deployment step results
all_results = integration.get_all_step_results()

# Get the status of the integration
status = integration.get_status()

# Cancel all running deployment steps
integration.cancel_all_steps()
```

## Concurrent Execution

The Codegen agent supports concurrent execution of tasks, allowing for parallel execution of deployment steps. This is achieved through the `ConcurrentExecutionEngine` class, which manages the execution of tasks in parallel using a thread pool.

The concurrent execution engine supports:

- Executing tasks in parallel with a configurable maximum number of concurrent tasks
- Monitoring the status of tasks
- Cancelling running tasks
- Handling task dependencies
- Prioritizing tasks based on dependencies

## Context Management

The Codegen agent uses a context manager to manage the context for tasks. The context manager provides:

- Project context management
- Task-specific context management
- Bidirectional context sharing between TaskWeaver and Codegen
- Context compression for efficient storage

## Requirements Management

The Codegen agent uses a requirements manager to parse requirements and create atomic tasks. The requirements manager provides:

- Parsing requirements from text
- Creating atomic tasks from requirements
- Identifying dependencies between tasks
- Prioritizing tasks based on dependencies
- Creating a dependency graph for tasks

## Integration with TaskWeaver

The Codegen agent integrates with TaskWeaver through the `CodegenWeaverIntegration` class, which provides a bridge between the TaskWeaver weaver component and the Codegen agent. This allows the weaver to call the Codegen agent for executing deployment steps.

The integration works as follows:

1. The weaver component calls the `set_project_context` method to set the project context for the Codegen agent
2. The weaver component calls the `parse_deployment_steps` method to parse deployment steps from a deployment plan
3. The weaver component calls the `execute_deployment_steps` method to execute the deployment steps
4. The weaver component can monitor the status of the deployment steps using the `get_step_status` and `get_step_result` methods

