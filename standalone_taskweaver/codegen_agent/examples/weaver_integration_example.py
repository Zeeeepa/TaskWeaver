#!/usr/bin/env python3
"""
Example script demonstrating the integration between TaskWeaver and Codegen
"""

import os
import sys
import json
import time
import logging
from typing import Dict, List, Optional, Any

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))))

from standalone_taskweaver.app.app import TaskWeaverApp
from standalone_taskweaver.config.config_mgt import AppConfigSource
from standalone_taskweaver.logging import TelemetryLogger
from standalone_taskweaver.codegen_agent.integration import CodegenIntegration
from standalone_taskweaver.codegen_agent.weaver_integration import WeaverCodegenIntegration
from standalone_taskweaver.ui.taskweaver_ui_enhanced import TaskWeaverUIEnhanced

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("weaver-integration-example")

def main():
    """
    Main function demonstrating the integration between TaskWeaver and Codegen
    """
    # Create app
    app = TaskWeaverApp()
    
    # Create config
    config = AppConfigSource()
    
    # Create logger
    logger = TelemetryLogger()
    
    # Create UI
    ui = TaskWeaverUIEnhanced(app, config, logger)
    
    # Initialize integration
    # Replace these with your actual tokens
    github_token = os.environ.get("GITHUB_TOKEN", "your_github_token")
    codegen_token = os.environ.get("CODEGEN_TOKEN", "your_codegen_token")
    ngrok_token = os.environ.get("NGROK_TOKEN", "your_ngrok_token")
    codegen_org_id = os.environ.get("CODEGEN_ORG_ID", "your_codegen_org_id")
    
    success = ui.initialize_integration(
        github_token=github_token,
        codegen_token=codegen_token,
        ngrok_token=ngrok_token,
        codegen_org_id=codegen_org_id
    )
    
    if not success:
        logger.error("Failed to initialize integration")
        return
    
    logger.info("Integration initialized successfully")
    
    # Example 1: Check if a task is deployment-related
    task_description = "Deploy the application to AWS using Terraform"
    
    is_deployment = ui.is_deployment_task(task_description)
    
    logger.info(f"Is deployment task: {is_deployment}")
    
    # Example 2: Create a deployment task
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
    
    logger.info(f"Created deployment task with ID: {task_id}")
    
    # Example 3: Delegate the task to Codegen
    success = ui.delegate_deployment_task(task_id)
    
    if not success:
        logger.error("Failed to delegate task to Codegen")
        return
    
    logger.info("Task delegated to Codegen successfully")
    
    # Example 4: Monitor the task status
    while True:
        status = ui.get_deployment_task_status(task_id)
        
        logger.info(f"Task status: {status['status']}")
        
        if status["status"] in ["completed", "failed", "cancelled"]:
            break
        
        time.sleep(5)
    
    # Example 5: Get the task results
    results = ui.get_deployment_task_results(task_id)
    
    logger.info(f"Task results: {json.dumps(results, indent=2)}")
    
    # Example 6: Generate a deployment report
    report = ui.generate_deployment_report(task_id)
    
    logger.info(f"Deployment report: {json.dumps(report, indent=2)}")
    
    # Example 7: Add the results to TaskWeaver's memory
    planner_id = "example-planner"  # Replace with an actual planner ID
    
    try:
        success = ui.add_deployment_to_memory(task_id, planner_id)
        
        if success:
            logger.info("Results added to memory successfully")
        else:
            logger.error("Failed to add results to memory")
    except Exception as e:
        logger.error(f"Error adding results to memory: {str(e)}")
    
    # Example 8: List all deployment tasks
    tasks = ui.list_deployment_tasks()
    
    logger.info(f"All deployment tasks: {json.dumps(tasks, indent=2)}")

if __name__ == "__main__":
    main()

