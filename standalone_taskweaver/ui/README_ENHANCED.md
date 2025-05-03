# Enhanced TaskWeaver UI with Codegen Integration

This directory contains an enhanced version of the TaskWeaver UI with Codegen agent integration for executing deployment steps.

## Overview

The enhanced TaskWeaver UI provides a web interface for interacting with the Codegen agent, allowing users to:

1. Initialize the Codegen integration with API credentials
2. Set the project context for the Codegen agent
3. Parse deployment steps from a deployment plan
4. Execute deployment steps concurrently
5. Monitor the status of deployment steps
6. Execute individual deployment steps
7. Generate code, analyze code, refactor code, and generate tests using the Codegen API

## Components

- `taskweaver_ui_enhanced.py`: Enhanced TaskWeaver UI class with Codegen integration
- `server_enhanced.py`: Enhanced web server for the TaskWeaver UI
- `main_enhanced.py`: Main entry point for the enhanced TaskWeaver UI
- `run_enhanced.py`: Run script for the enhanced TaskWeaver UI
- `templates/index.html`: HTML template for the main UI
- `templates/codegen.html`: HTML template for the Codegen page

## Usage

To run the enhanced TaskWeaver UI:

```bash
python -m standalone_taskweaver.ui.run_enhanced
```

This will start the web server on `http://0.0.0.0:8000`.

## API Endpoints

### Initialization

- `POST /api/codegen/initialize`: Initialize Codegen integration
- `GET /api/codegen/status`: Get the status of the Codegen integration
- `GET /api/codegen/repositories`: Get list of GitHub repositories
- `POST /api/codegen/repository`: Set the active GitHub repository

### Project Context

- `POST /api/weaver/project-context`: Set the project context for the Codegen agent

### Deployment Steps

- `POST /api/weaver/deployment-steps`: Parse deployment steps from a deployment plan
- `POST /api/weaver/execute-steps`: Execute deployment steps
- `POST /api/weaver/execute-step`: Execute a single deployment step
- `GET /api/weaver/step/{step_id}/status`: Get the status of a deployment step
- `GET /api/weaver/step/{step_id}/result`: Get the result of a deployment step
- `GET /api/weaver/steps/results`: Get all deployment step results
- `GET /api/weaver/status`: Get the status of the weaver integration
- `POST /api/weaver/cancel`: Cancel all running deployment steps

### Code Generation

- `POST /api/codegen/generate-code`: Generate code using Codegen
- `POST /api/codegen/analyze-code`: Analyze code using Codegen
- `POST /api/codegen/refactor-code`: Refactor code using Codegen
- `POST /api/codegen/generate-tests`: Generate tests for code using Codegen

### Context Management

- `GET /api/codegen/context`: Get shared context between TaskWeaver and Codegen
- `POST /api/codegen/context/taskweaver`: Update TaskWeaver context
- `POST /api/codegen/context/codegen`: Update Codegen context
- `POST /api/codegen/context/issue`: Add a GitHub issue to the context
- `POST /api/codegen/context/pr`: Add a GitHub pull request to the context
- `POST /api/codegen/context/file`: Add a file to the context

## Integration with TaskWeaver

The enhanced TaskWeaver UI integrates with the TaskWeaver framework through the `CodegenWeaverIntegration` class, which provides a bridge between the TaskWeaver weaver component and the Codegen agent. This allows the weaver to call the Codegen agent for executing deployment steps.

The integration works as follows:

1. The weaver component calls the `set_project_context` method to set the project context for the Codegen agent
2. The weaver component calls the `parse_deployment_steps` method to parse deployment steps from a deployment plan
3. The weaver component calls the `execute_deployment_steps` method to execute the deployment steps
4. The weaver component can monitor the status of the deployment steps using the `get_step_status` and `get_step_result` methods

## Example Usage

Here's an example of how to use the enhanced TaskWeaver UI from Python:

```python
from standalone_taskweaver.ui.taskweaver_ui_enhanced import TaskWeaverUIEnhanced

# Create a TaskWeaverUIEnhanced instance
ui = TaskWeaverUIEnhanced(app, config, logger)

# Initialize Codegen integration
ui.initialize_integration(
    github_token="your-github-token",
    codegen_token="your-codegen-token",
    ngrok_token="your-ngrok-token",
    codegen_org_id="your-codegen-org-id"
)

# Set the project context
ui.set_project_context(
    project_name="My Project",
    project_description="A sample project",
    requirements_text="This project requires..."
)

# Parse deployment steps
steps = ui.parse_deployment_steps("""
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
""")

# Execute deployment steps
ui.execute_deployment_steps(max_concurrent_steps=2)

# Monitor the status of the deployment steps
for step in steps:
    status = ui.get_step_status(step.id)
    print(f"Step {step.id}: {status}")
```

