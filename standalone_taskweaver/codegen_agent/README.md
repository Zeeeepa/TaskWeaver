# TaskWeaver Codegen Integration

This module provides integration between TaskWeaver and Codegen, allowing you to use Codegen's AI-powered code generation capabilities within TaskWeaver.

## Overview

The integration consists of the following components:

1. **Codegen Agent**: A wrapper around the Codegen SDK that provides a simple interface for creating and managing Codegen tasks.
2. **Integration Layer**: A class that connects TaskWeaver with Codegen, GitHub, and ngrok.
3. **UI Components**: A web interface for interacting with the integration.

## Features

- Connect to GitHub, Codegen, and ngrok APIs
- Browse and select GitHub repositories
- Create and manage Codegen tasks
- Generate requirements documentation
- Start and stop automated workflows
- Track task status and results

## Setup

### Prerequisites

- GitHub API token
- Codegen API token
- ngrok API token
- Codegen organization ID

### Installation

1. Ensure you have TaskWeaver installed
2. Install the required dependencies:

```bash
pip install codegen-sdk github pyngrok
```

### Configuration

You can configure the integration through the UI or programmatically:

```python
from standalone_taskweaver.codegen_agent.integration import CodegenIntegration

# Create integration instance
integration = CodegenIntegration(app, config, logger)

# Initialize with API credentials
integration.initialize(
    github_token="your_github_token",
    codegen_token="your_codegen_token",
    ngrok_token="your_ngrok_token",
    codegen_org_id="your_codegen_org_id",
    repo_name="your_repo_name"  # Optional
)

# Set repository
integration.set_repository("owner/repo")

# Get repositories
repos = integration.get_repositories()

# Create a Codegen task
task_id = integration.create_codegen_task("Implement a login form with validation")

# Get task status
status = integration.get_task_status(task_id)

# Start workflow
integration.start_workflow()

# Stop workflow
integration.stop_workflow()
```

## UI Usage

The integration includes a web UI that allows you to:

1. Set up API credentials
2. Browse and select GitHub repositories
3. Chat with TaskWeaver to generate requirements
4. Create and manage Codegen tasks
5. Track task status and results

To start the UI:

```bash
python -m standalone_taskweaver.ui.run
```

Then open your browser to http://localhost:8000

## Architecture

The integration follows this architecture:

```
TaskWeaver App
    |
    ├── CodegenIntegration
    |       |
    |       ├── GitHubManager
    |       ├── CodegenManager
    |       ├── NgrokManager
    |       └── WorkflowManager
    |
    └── UI
        |
        ├── Setup
        ├── Chat
        ├── Requirements
        ├── Codegen
        └── Tasks
```

## Workflow

A typical workflow using this integration:

1. Set up API credentials
2. Select a GitHub repository
3. Chat with TaskWeaver to define requirements
4. Generate a requirements document
5. Send the requirements to Codegen
6. Track the task status
7. Review and merge the generated code

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

