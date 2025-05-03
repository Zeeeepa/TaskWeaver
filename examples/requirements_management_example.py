#!/usr/bin/env python3
"""
Example script demonstrating how to use the requirements management functionality
"""

import os
import sys
import json
import logging
from pathlib import Path

# Add the parent directory to the Python path
sys.path.append(str(Path(__file__).parent.parent))

from standalone_taskweaver.app.app import TaskWeaverApp
from standalone_taskweaver.config.config_mgt import AppConfigSource
from standalone_taskweaver.logging import TelemetryLogger
from standalone_taskweaver.codegen_agent.integration import CodegenIntegration
from standalone_taskweaver.codegen_agent.requirements_manager import RequirementsManager

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("requirements-example")

def main():
    """
    Main entry point
    """
    # Get environment variables
    github_token = os.environ.get("GITHUB_TOKEN")
    codegen_token = os.environ.get("CODEGEN_TOKEN")
    ngrok_token = os.environ.get("NGROK_TOKEN")
    codegen_org_id = os.environ.get("CODEGEN_ORG_ID")
    repo_name = os.environ.get("REPO_NAME")
    
    if not all([github_token, codegen_token, ngrok_token, codegen_org_id, repo_name]):
        logger.error("Missing required environment variables")
        return 1
    
    # Initialize the app
    app = TaskWeaverApp()
    config = AppConfigSource()
    logger = TelemetryLogger()
    
    # Initialize the integration
    integration = CodegenIntegration(app, config, logger)
    success = integration.initialize(
        github_token=github_token,
        codegen_token=codegen_token,
        ngrok_token=ngrok_token,
        codegen_org_id=codegen_org_id,
        repo_name=repo_name
    )
    
    if not success:
        logger.error("Failed to initialize Codegen integration")
        return 1
    
    # Initialize the requirements manager
    requirements_manager = RequirementsManager(app, config, logger, integration)
    
    # Example requirements
    project_name = "TaskWeaver-Codegen Integration"
    requirements = """
# Core Requirements

1. TaskWeaver should be able to create and update a REQUIREMENTS.md file in the repository.
2. The REQUIREMENTS.md file should contain sections for requirements, current structure, and UI mockups.
3. TaskWeaver should be able to parse the REQUIREMENTS.md file to extract requirements.
4. TaskWeaver should break down requirements into atomic tasks for concurrent execution.
5. TaskWeaver should identify dependencies between tasks.
6. TaskWeaver should group tasks into phases based on dependencies.
7. TaskWeaver should generate concurrent queries for each phase.
8. TaskWeaver should provide a command-line interface for managing requirements.
9. TaskWeaver should integrate with Codegen to execute tasks concurrently.
10. TaskWeaver should provide feedback on task execution.

# Interface Requirements

1. TaskWeaver should provide a clear API for creating and updating requirements.
2. TaskWeaver should provide a clear API for parsing requirements.
3. TaskWeaver should provide a clear API for generating concurrent queries.
4. TaskWeaver should provide a clear API for executing concurrent queries.
5. TaskWeaver should provide a clear API for monitoring task execution.
"""
    
    current_structure = """
# Current Structure

- standalone_taskweaver/
  - app/
  - code_interpreter/
  - codegen_agent/
    - bidirectional_context.py
    - codegen.py
    - codegen_issue_solver.py
    - context_manager.py
    - integration.py
    - planner_integration.py
  - common/
  - config/
  - llm/
  - logging/
  - memory/
  - module/
  - planner/
  - role/
  - session/
  - ui/
  - utils/
"""
    
    ui_mockup = """
# UI Mockup

```
+------------------------------------------+
|                TaskWeaver                |
+------------------------------------------+
| Project: [Project Name]                  |
+------------------------------------------+
| Requirements | Structure | Tasks | Queries|
+------------------------------------------+
|                                          |
| # Requirements                           |
|                                          |
| 1. Requirement 1                         |
| 2. Requirement 2                         |
| 3. Requirement 3                         |
|                                          |
+------------------------------------------+
| Create | Parse | Generate | Execute      |
+------------------------------------------+
```
"""
    
    # Create the requirements document
    logger.info("Creating requirements document...")
    success, error = requirements_manager.create_requirements_document(
        project_name=project_name,
        requirements=requirements,
        current_structure=current_structure,
        ui_mockup=ui_mockup
    )
    
    if not success:
        logger.error(f"Failed to create requirements document: {error}")
        return 1
    
    logger.info("Requirements document created successfully")
    
    # Parse the requirements document
    logger.info("Parsing requirements document...")
    parsed_requirements = integration.parse_requirements_document()
    
    if not parsed_requirements:
        logger.error("Failed to parse requirements document")
        return 1
    
    logger.info("Requirements document parsed successfully")
    logger.info(f"Found {len(parsed_requirements.get('atomic_tasks', []))} atomic tasks")
    logger.info(f"Found {len(parsed_requirements.get('phases', []))} phases")
    
    # Generate concurrent queries
    logger.info("Generating concurrent queries for phase 1...")
    queries = integration.generate_concurrent_queries(phase=1)
    
    if not queries:
        logger.error("Failed to generate concurrent queries")
        return 1
    
    logger.info(f"Generated {len(queries)} concurrent queries")
    
    # Print the first query
    if queries:
        logger.info("First query:")
        logger.info(queries[0])
    
    return 0

if __name__ == "__main__":
    sys.exit(main())

