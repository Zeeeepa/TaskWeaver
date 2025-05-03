# TaskWeaver-Codegen Integration

This document provides an overview of the integration between TaskWeaver and Codegen for deployment tasks.

## Overview

The TaskWeaver-Codegen integration allows TaskWeaver to delegate deployment-related tasks to Codegen, which can execute them efficiently and report back the results. This integration enables TaskWeaver to handle complex deployment scenarios by leveraging Codegen's capabilities for code generation, infrastructure management, and deployment automation.

## Components

The integration consists of the following components:

1. **WeaverCodegenIntegration**: A bridge between TaskWeaver's planner and the Codegen agent, allowing TaskWeaver to delegate deployment tasks to Codegen and monitor their progress.

2. **TaskWeaverUIEnhanced**: An enhanced version of the TaskWeaver UI that includes methods for deployment tasks.

3. **TaskWeaverServerEnhanced**: An enhanced version of the TaskWeaver server that adds new API endpoints for deployment operations.

4. **DeploymentTask**: A representation of a deployment task, including its description, context, status, and results.

## Features

The integration provides the following features:

- **Deployment Task Detection**: Automatically detect if a task is deployment-related based on keywords in the task description.

- **Task Delegation**: Delegate deployment tasks to Codegen for execution.

- **Task Monitoring**: Monitor the status and progress of deployment tasks.

- **Result Retrieval**: Retrieve the results of deployment tasks, including success/failure status and detailed output.

- **Report Generation**: Generate comprehensive deployment reports based on task results.

- **Memory Integration**: Add deployment task results to TaskWeaver's memory for future reference.

## API Endpoints

The integration adds the following API endpoints to the TaskWeaver server:

- **POST /api/codegen/deployment/is-deployment-task**: Determine if a task is deployment-related.
- **POST /api/codegen/deployment/create**: Create a deployment task.
- **POST /api/codegen/deployment/delegate**: Delegate a deployment task to Codegen.
- **GET /api/codegen/deployment/status**: Get the status of a deployment task.
- **GET /api/codegen/deployment/results**: Get the results of a deployment task.
- **GET /api/codegen/deployment/report**: Generate a report for a deployment task.
- **POST /api/codegen/deployment/add-to-memory**: Add deployment task results to TaskWeaver's memory.
- **POST /api/codegen/deployment/cancel**: Cancel a deployment task.
- **GET /api/codegen/deployment/list**: List all deployment tasks.

## Usage

### Initialization

Before using the integration, you need to initialize it with the necessary API credentials:

```python
from standalone_taskweaver.app.app import TaskWeaverApp
from standalone_taskweaver.config.config_mgt import AppConfigSource
from standalone_taskweaver.logging import TelemetryLogger
from standalone_taskweaver.ui.taskweaver_ui_enhanced import TaskWeaverUIEnhanced

# Create app, config, and logger
app = TaskWeaverApp()
config = AppConfigSource()
logger = TelemetryLogger()

# Create UI
ui = TaskWeaverUIEnhanced(app, config, logger)

# Initialize integration
success = ui.initialize_integration(
    github_token="your_github_token",
    codegen_token="your_codegen_token",
    ngrok_token="your_ngrok_token",
    codegen_org_id="your_codegen_org_id"
)
```

### Checking if a Task is Deployment-Related

```python
task_description = "Deploy the application to AWS using Terraform"
is_deployment = ui.is_deployment_task(task_description)
```

### Creating a Deployment Task

```python
context = {
    "repository": "example-repo",
    "branch": "main",
    "environment": "production",
    "infrastructure": {
        "provider": "aws",
        "region": "us-west-2",
        "services": ["ec2", "rds", "s3"]
    }
}

task_id = ui.create_deployment_task(task_description, context)
```

### Delegating a Task to Codegen

```python
success = ui.delegate_deployment_task(task_id)
```

### Monitoring Task Status

```python
status = ui.get_deployment_task_status(task_id)
```

### Getting Task Results

```python
results = ui.get_deployment_task_results(task_id)
```

### Generating a Deployment Report

```python
report = ui.generate_deployment_report(task_id)
```

### Adding Results to TaskWeaver's Memory

```python
success = ui.add_deployment_to_memory(task_id, planner_id)
```

### Listing All Deployment Tasks

```python
tasks = ui.list_deployment_tasks()
```

## Example

See the `weaver_integration_example.py` script in the `examples` directory for a complete example of using the integration.

## Architecture

The integration follows a layered architecture:

1. **UI Layer**: The `TaskWeaverUIEnhanced` class provides a high-level interface for interacting with the integration.

2. **Integration Layer**: The `WeaverCodegenIntegration` class provides the core functionality for delegating tasks to Codegen and monitoring their progress.

3. **Execution Layer**: The Codegen agent executes the deployment tasks and reports back the results.

4. **API Layer**: The `TaskWeaverServerEnhanced` class exposes the integration functionality through REST API endpoints.

## Workflow

The typical workflow for using the integration is as follows:

1. TaskWeaver receives a task from the user.
2. TaskWeaver's planner determines if the task is deployment-related.
3. If the task is deployment-related, TaskWeaver creates a deployment task and delegates it to Codegen.
4. Codegen breaks down the task into atomic steps and executes them.
5. TaskWeaver monitors the progress of the task and retrieves the results when it's completed.
6. TaskWeaver generates a report based on the results and adds them to its memory.
7. TaskWeaver presents the results to the user.

## Conclusion

The TaskWeaver-Codegen integration provides a powerful way to handle deployment tasks in TaskWeaver by leveraging Codegen's capabilities. It enables TaskWeaver to automate complex deployment scenarios and provide detailed feedback to the user.

