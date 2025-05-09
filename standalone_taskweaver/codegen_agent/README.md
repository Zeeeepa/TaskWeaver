# TaskWeaver Codegen Integration

This module provides integration between TaskWeaver and Codegen, allowing you to use Codegen's AI-powered code generation capabilities within TaskWeaver.

## Overview

The integration consists of the following components:

1. **Codegen Agent**: A wrapper around the Codegen SDK that provides a simple interface for creating and managing Codegen tasks.
2. **Integration Layer**: A class that connects TaskWeaver with Codegen, GitHub, and ngrok.
3. **Bidirectional Context Manager**: A component that maintains a shared understanding between TaskWeaver and Codegen.
4. **Planner Integration**: A component that allows TaskWeaver's planner to delegate code-related tasks to Codegen.
5. **Advanced API**: A more granular API for leveraging specific Codegen capabilities.
6. **UI Components**: A web interface for interacting with the integration.

## Features

- Connect to GitHub, Codegen, and ngrok APIs
- Browse and select GitHub repositories
- Create and manage Codegen tasks
- Generate requirements documentation
- Start and stop automated workflows
- Track task status and results
- Bidirectional context sharing between TaskWeaver and Codegen
- Delegate code-related tasks from TaskWeaver's planner to Codegen
- Advanced code generation, analysis, refactoring, and testing capabilities
- Interactive UI for code viewing, editing, and generation

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

## Advanced Usage

### Bidirectional Context Manager

The bidirectional context manager maintains a shared understanding between TaskWeaver and Codegen:

```python
from standalone_taskweaver.codegen_agent.bidirectional_context import BidirectionalContext

# Create context manager
context_manager = BidirectionalContext(app, config, logger, memory)

# Initialize context manager
context_manager.initialize()

# Get shared context
shared_context = context_manager.get_shared_context()

# Update TaskWeaver context
context_manager.update_taskweaver_context({"key": "value"})

# Update Codegen context
context_manager.update_codegen_context({"key": "value"})

# Add GitHub issue to context
context_manager.add_issue_to_context(123)

# Add GitHub PR to context
context_manager.add_pr_to_context(456)

# Add file to context
context_manager.add_file_to_context("path/to/file.py")

# Export context for Codegen
codegen_context = context_manager.export_context_for_codegen()

# Export context for TaskWeaver
taskweaver_context = context_manager.export_context_for_taskweaver()
```

### Planner Integration

The planner integration allows TaskWeaver's planner to delegate code-related tasks to Codegen:

```python
from standalone_taskweaver.codegen_agent.planner_integration import CodegenPlannerIntegration

# Create planner integration
planner_integration = CodegenPlannerIntegration(app, config, logger, codegen_integration)

# Check if a task is code-related
is_code_related = planner_integration.is_code_related_task("Implement a login form")

# Delegate a task to Codegen
result = planner_integration.delegate_to_codegen("Implement a login form", context)

# Incorporate Codegen result into the planner
planner_integration.incorporate_codegen_result(planner, task_id, result)
```

### Advanced API

The advanced API provides more granular control over Codegen's capabilities:

```python
from standalone_taskweaver.codegen_agent.advanced_api import CodegenAdvancedAPI

# Create advanced API
advanced_api = CodegenAdvancedAPI(app, config, logger, codegen_integration, context_manager)

# Generate code
result = advanced_api.generate_code("Create a function to calculate factorial", "python")

# Analyze code
result = advanced_api.analyze_code("def factorial(n):\n    return 1 if n <= 1 else n * factorial(n-1)", "python")

# Refactor code
result = advanced_api.refactor_code("def factorial(n):\n    return 1 if n <= 1 else n * factorial(n-1)", "python", "Use iteration instead of recursion")

# Generate tests
result = advanced_api.generate_tests("def factorial(n):\n    return 1 if n <= 1 else n * factorial(n-1)", "python")
```

## UI Usage

The integration includes a web UI that allows you to:

1. Set up API credentials
2. Browse and select GitHub repositories
3. Chat with TaskWeaver to generate requirements
4. Create and manage Codegen tasks
5. Track task status and results
6. Generate, analyze, refactor, and test code
7. View and manage shared context

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
    ├── BidirectionalContext
    |       |
    |       ├── TaskWeaverContext
    |       ├── CodegenContext
    |       └── SharedContext
    |
    ├── CodegenPlannerIntegration
    |       |
    |       ├── TaskDetection
    |       ├── TaskDelegation
    |       └── ResultIncorporation
    |
    ├── CodegenAdvancedAPI
    |       |
    |       ├── CodeGeneration
    |       ├── CodeAnalysis
    |       ├── CodeRefactoring
    |       └── TestGeneration
    |
    └── UI
        |
        ├── Setup
        ├── Chat
        ├── Requirements
        ├── Codegen
        ├── Tasks
        └── Context
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
8. Use advanced features for code generation, analysis, refactoring, and testing

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.
