# Enhanced Codegen Agent with Weaver Integration

This directory contains an enhanced version of the Codegen agent implementation for TaskWeaver with integration for the weaver component.

## Overview

The enhanced Codegen agent provides a comprehensive implementation of the Codegen agent that supports integration with TaskWeaver's weaver component for executing deployment steps. It allows the weaver to call the Codegen agent for executing deployment steps, making it ideal for automating deployment processes.

## Components

- `weaver_integration.py`: Integration between TaskWeaver's weaver component and the Codegen agent
- `codegen_agent.py`: Main Codegen agent implementation
- `concurrent_execution.py`: Concurrent execution engine for executing tasks in parallel
- `concurrent_context_manager.py`: Context manager for managing context in concurrent execution
- `requirements_manager.py`: Manager for parsing requirements and creating atomic tasks
- `bidirectional_context.py`: Bidirectional context manager for sharing context between TaskWeaver and Codegen
- `planner_integration.py`: Integration between TaskWeaver's planner and Codegen
- `integration.py`: Integration between Codegen and TaskWeaver
- `interface_generator.py`: Generator for interfaces and mock implementations
- `query_generation.py`: Framework for generating optimized queries
- `advanced_api.py`: Advanced API for Codegen

## Weaver Integration

The `CodegenWeaverIntegration` class provides a bridge between TaskWeaver's weaver component and the Codegen agent. It allows the weaver to call the Codegen agent for executing deployment steps.

### Key Features

- **Project Context Management**: Set the project context for the Codegen agent
- **Deployment Step Parsing**: Parse deployment steps from a deployment plan
- **Concurrent Execution**: Execute deployment steps concurrently
- **Status Monitoring**: Monitor the status of deployment steps
- **Result Retrieval**: Retrieve the results of deployment steps
- **Cancellation**: Cancel running deployment steps

### Usage

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

## Integration with TaskWeaver UI

The Codegen agent with weaver integration is designed to work seamlessly with the enhanced TaskWeaver UI. The UI provides a web interface for interacting with the Codegen agent, allowing users to:

1. Initialize the Codegen integration with API credentials
2. Set the project context for the Codegen agent
3. Parse deployment steps from a deployment plan
4. Execute deployment steps concurrently
5. Monitor the status of deployment steps
6. Execute individual deployment steps

## Deployment Step Parsing

The `parse_deployment_steps` method parses a deployment plan into atomic tasks that can be executed by the Codegen agent. The deployment plan should be a text document with steps in the following format:

```
Step 1: Initialize the project
Create a new directory and initialize a Git repository.

Step 2: Install dependencies
Install the required dependencies using npm.

Step 3: Configure the application
Create a configuration file with the required settings.

Step 4: Build the application
Build the application using the build script.

Step 5: Deploy the application
Deploy the application to the production server.
```

Each step is parsed into an `AtomicTask` object with the following properties:

- `id`: A unique identifier for the step
- `title`: The title of the step
- `description`: The description of the step
- `priority`: The priority of the step
- `dependencies`: The dependencies of the step
- `phase`: The phase of the step
- `status`: The status of the step
- `tags`: The tags of the step
- `estimated_time`: The estimated time to complete the step
- `assignee`: The assignee of the step
- `interface_definition`: Whether the step is an interface definition

## Concurrent Execution

The Codegen agent supports concurrent execution of deployment steps, allowing for parallel execution of steps that do not have dependencies on each other. This is achieved through the `ConcurrentExecutionEngine` class, which manages the execution of steps in parallel using a thread pool.

The concurrent execution engine supports:

- Executing steps in parallel with a configurable maximum number of concurrent steps
- Monitoring the status of steps
- Cancelling running steps
- Handling step dependencies
- Prioritizing steps based on dependencies

## Context Management

The Codegen agent uses a context manager to manage the context for deployment steps. The context manager provides:

- Project context management
- Step-specific context management
- Bidirectional context sharing between TaskWeaver and Codegen
- Context compression for efficient storage

## Requirements Management

The Codegen agent uses a requirements manager to parse requirements and create atomic tasks. The requirements manager provides:

- Parsing requirements from text
- Creating atomic tasks from requirements
- Identifying dependencies between tasks
- Prioritizing tasks based on dependencies
- Creating a dependency graph for tasks

