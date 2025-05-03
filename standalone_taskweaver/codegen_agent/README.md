# Codegen Agent Integration for TaskWeaver

This module provides integration between TaskWeaver and Codegen, allowing TaskWeaver to leverage Codegen's code generation capabilities for implementing tasks.

## Overview

The integration consists of several components:

- **Integration**: Core integration with Codegen API
- **Planner Integration**: Integration with TaskWeaver's planner
- **Bidirectional Context**: Context sharing between systems
- **Requirements Management**: Creation and parsing of requirements documents
- **Concurrent Execution**: Execution of tasks concurrently

## Requirements Management

The requirements management functionality allows TaskWeaver to:

1. Create and update a REQUIREMENTS.md file in the repository
2. Parse the REQUIREMENTS.md file to extract requirements
3. Break down requirements into atomic tasks for concurrent execution
4. Identify dependencies between tasks
5. Group tasks into phases based on dependencies
6. Generate concurrent queries for each phase

### Creating a Requirements Document

```python
from standalone_taskweaver.app.app import TaskWeaverApp
from standalone_taskweaver.config.config_mgt import AppConfigSource
from standalone_taskweaver.logging import TelemetryLogger
from standalone_taskweaver.codegen_agent.integration import CodegenIntegration
from standalone_taskweaver.codegen_agent.requirements_manager import RequirementsManager

# Initialize the app
app = TaskWeaverApp()
config = AppConfigSource()
logger = TelemetryLogger()

# Initialize the integration
integration = CodegenIntegration(app, config, logger)
integration.initialize(
    github_token="your-github-token",
    codegen_token="your-codegen-token",
    ngrok_token="your-ngrok-token",
    codegen_org_id="your-codegen-org-id",
    repo_name="your-repo-name"
)

# Initialize the requirements manager
requirements_manager = RequirementsManager(app, config, logger, integration)

# Create the requirements document
success, error = requirements_manager.create_requirements_document(
    project_name="Your Project",
    requirements="Your requirements",
    current_structure="Your current structure",
    ui_mockup="Your UI mockup"
)
```

### Parsing a Requirements Document

```python
# Parse the requirements document
parsed_requirements = integration.parse_requirements_document()

# Access the parsed requirements
atomic_tasks = parsed_requirements.get("atomic_tasks", [])
phases = parsed_requirements.get("phases", [])
```

### Generating Concurrent Queries

```python
# Generate concurrent queries for phase 1
queries = integration.generate_concurrent_queries(phase=1)
```

## Command-Line Interface

The module also provides a command-line interface for managing requirements:

```bash
# Create a requirements document
python -m standalone_taskweaver.codegen_agent.requirements_cli create \
    --github-token your-github-token \
    --codegen-token your-codegen-token \
    --ngrok-token your-ngrok-token \
    --codegen-org-id your-codegen-org-id \
    --repo-name your-repo-name \
    --project-name "Your Project" \
    --requirements-file requirements.txt \
    --structure-file structure.txt \
    --ui-mockup-file ui_mockup.txt

# Parse a requirements document
python -m standalone_taskweaver.codegen_agent.requirements_cli parse \
    --github-token your-github-token \
    --codegen-token your-codegen-token \
    --ngrok-token your-ngrok-token \
    --codegen-org-id your-codegen-org-id \
    --repo-name your-repo-name \
    --output-file parsed_requirements.json

# Generate concurrent queries
python -m standalone_taskweaver.codegen_agent.requirements_cli generate \
    --github-token your-github-token \
    --codegen-token your-codegen-token \
    --ngrok-token your-ngrok-token \
    --codegen-org-id your-codegen-org-id \
    --repo-name your-repo-name \
    --phase 1 \
    --output-file queries.json
```

## Example

See the `examples/requirements_management_example.py` file for a complete example of how to use the requirements management functionality.
