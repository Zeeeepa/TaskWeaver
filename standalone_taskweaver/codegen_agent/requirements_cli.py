#!/usr/bin/env python3
"""
Command-line interface for managing requirements documents
"""

import os
import sys
import json
import logging
import argparse
from typing import Dict, List, Optional, Any, Union, Tuple
from pathlib import Path

from standalone_taskweaver.app.app import TaskWeaverApp
from standalone_taskweaver.config.config_mgt import AppConfigSource
from standalone_taskweaver.logging import TelemetryLogger
from standalone_taskweaver.codegen_agent.integration import CodegenIntegration
from standalone_taskweaver.codegen_agent.requirements_manager import RequirementsManager

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("requirements-cli")

def get_token_from_env_or_arg(arg_value: Optional[str], env_var: str, description: str) -> Optional[str]:
    """
    Get a token from environment variable or command line argument
    
    Args:
        arg_value: Value from command line argument
        env_var: Environment variable name
        description: Description of the token for error messages
        
    Returns:
        Optional[str]: Token value or None if not found
    """
    if arg_value:
        return arg_value
    
    env_value = os.environ.get(env_var)
    if env_value:
        return env_value
    
    logger.error(f"{description} not provided. Please set {env_var} environment variable or use the command line argument.")
    return None

def create_requirements_document(args):
    """
    Create a requirements document
    """
    # Get tokens from environment variables or command line arguments
    github_token = get_token_from_env_or_arg(args.github_token, "GITHUB_TOKEN", "GitHub token")
    codegen_token = get_token_from_env_or_arg(args.codegen_token, "CODEGEN_TOKEN", "Codegen token")
    ngrok_token = get_token_from_env_or_arg(args.ngrok_token, "NGROK_TOKEN", "ngrok token")
    codegen_org_id = get_token_from_env_or_arg(args.codegen_org_id, "CODEGEN_ORG_ID", "Codegen organization ID")
    repo_name = get_token_from_env_or_arg(args.repo_name, "REPO_NAME", "Repository name")
    
    if not all([github_token, codegen_token, ngrok_token, codegen_org_id, repo_name]):
        return 1
    
    # Initialize the app
    app = TaskWeaverApp()
    config = AppConfigSource()
    telemetry_logger = TelemetryLogger()
    
    # Initialize the integration
    integration = CodegenIntegration(app, config, telemetry_logger)
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
    requirements_manager = RequirementsManager(app, config, telemetry_logger, integration)
    
    # Read requirements content
    requirements_content = ""
    if args.requirements_file:
        with open(args.requirements_file, "r") as f:
            requirements_content = f.read()
    else:
        requirements_content = args.requirements
    
    # Read current structure content
    current_structure = None
    if args.structure_file:
        with open(args.structure_file, "r") as f:
            current_structure = f.read()
    
    # Read UI mockup content
    ui_mockup = None
    if args.ui_mockup_file:
        with open(args.ui_mockup_file, "r") as f:
            ui_mockup = f.read()
    
    # Create the requirements document
    success, error = requirements_manager.create_requirements_document(
        project_name=args.project_name,
        requirements=requirements_content,
        current_structure=current_structure,
        ui_mockup=ui_mockup
    )
    
    if success:
        logger.info("Requirements document created successfully")
        return 0
    else:
        logger.error(f"Failed to create requirements document: {error}")
        return 1

def parse_requirements_document(args):
    """
    Parse a requirements document
    """
    # Get tokens from environment variables or command line arguments
    github_token = get_token_from_env_or_arg(args.github_token, "GITHUB_TOKEN", "GitHub token")
    codegen_token = get_token_from_env_or_arg(args.codegen_token, "CODEGEN_TOKEN", "Codegen token")
    ngrok_token = get_token_from_env_or_arg(args.ngrok_token, "NGROK_TOKEN", "ngrok token")
    codegen_org_id = get_token_from_env_or_arg(args.codegen_org_id, "CODEGEN_ORG_ID", "Codegen organization ID")
    repo_name = get_token_from_env_or_arg(args.repo_name, "REPO_NAME", "Repository name")
    
    if not all([github_token, codegen_token, ngrok_token, codegen_org_id, repo_name]):
        return 1
    
    # Initialize the app
    app = TaskWeaverApp()
    config = AppConfigSource()
    telemetry_logger = TelemetryLogger()
    
    # Initialize the integration
    integration = CodegenIntegration(app, config, telemetry_logger)
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
    
    # Parse the requirements document
    parsed_requirements = integration.parse_requirements_document()
    
    if not parsed_requirements:
        logger.error("Failed to parse requirements document")
        return 1
    
    # Print the parsed requirements
    if args.output_file:
        with open(args.output_file, "w") as f:
            json.dump(parsed_requirements, f, indent=2)
    else:
        print(json.dumps(parsed_requirements, indent=2))
    
    return 0

def generate_concurrent_queries(args):
    """
    Generate concurrent queries for a specific phase
    """
    # Get tokens from environment variables or command line arguments
    github_token = get_token_from_env_or_arg(args.github_token, "GITHUB_TOKEN", "GitHub token")
    codegen_token = get_token_from_env_or_arg(args.codegen_token, "CODEGEN_TOKEN", "Codegen token")
    ngrok_token = get_token_from_env_or_arg(args.ngrok_token, "NGROK_TOKEN", "ngrok token")
    codegen_org_id = get_token_from_env_or_arg(args.codegen_org_id, "CODEGEN_ORG_ID", "Codegen organization ID")
    repo_name = get_token_from_env_or_arg(args.repo_name, "REPO_NAME", "Repository name")
    
    if not all([github_token, codegen_token, ngrok_token, codegen_org_id, repo_name]):
        return 1
    
    # Initialize the app
    app = TaskWeaverApp()
    config = AppConfigSource()
    telemetry_logger = TelemetryLogger()
    
    # Initialize the integration
    integration = CodegenIntegration(app, config, telemetry_logger)
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
    
    # Generate concurrent queries
    queries = integration.generate_concurrent_queries(args.phase)
    
    if not queries:
        logger.error("Failed to generate concurrent queries")
        return 1
    
    # Print the queries
    if args.output_file:
        with open(args.output_file, "w") as f:
            json.dump(queries, f, indent=2)
    else:
        print(json.dumps(queries, indent=2))
    
    return 0

def main():
    """
    Main entry point
    """
    parser = argparse.ArgumentParser(description="Requirements management CLI")
    subparsers = parser.add_subparsers(dest="command", help="Command to run")
    
    # Create requirements document
    create_parser = subparsers.add_parser("create", help="Create a requirements document")
    create_parser.add_argument("--github-token", help="GitHub API token (or set GITHUB_TOKEN env var)")
    create_parser.add_argument("--codegen-token", help="Codegen API token (or set CODEGEN_TOKEN env var)")
    create_parser.add_argument("--ngrok-token", help="ngrok API token (or set NGROK_TOKEN env var)")
    create_parser.add_argument("--codegen-org-id", help="Codegen organization ID (or set CODEGEN_ORG_ID env var)")
    create_parser.add_argument("--repo-name", help="GitHub repository name (or set REPO_NAME env var)")
    create_parser.add_argument("--project-name", required=True, help="Project name")
    create_parser.add_argument("--requirements", help="Requirements content")
    create_parser.add_argument("--requirements-file", help="Path to requirements file")
    create_parser.add_argument("--structure-file", help="Path to current structure file")
    create_parser.add_argument("--ui-mockup-file", help="Path to UI mockup file")
    
    # Parse requirements document
    parse_parser = subparsers.add_parser("parse", help="Parse a requirements document")
    parse_parser.add_argument("--github-token", help="GitHub API token (or set GITHUB_TOKEN env var)")
    parse_parser.add_argument("--codegen-token", help="Codegen API token (or set CODEGEN_TOKEN env var)")
    parse_parser.add_argument("--ngrok-token", help="ngrok API token (or set NGROK_TOKEN env var)")
    parse_parser.add_argument("--codegen-org-id", help="Codegen organization ID (or set CODEGEN_ORG_ID env var)")
    parse_parser.add_argument("--repo-name", help="GitHub repository name (or set REPO_NAME env var)")
    parse_parser.add_argument("--output-file", help="Path to output file")
    
    # Generate concurrent queries
    generate_parser = subparsers.add_parser("generate", help="Generate concurrent queries")
    generate_parser.add_argument("--github-token", help="GitHub API token (or set GITHUB_TOKEN env var)")
    generate_parser.add_argument("--codegen-token", help="Codegen API token (or set CODEGEN_TOKEN env var)")
    generate_parser.add_argument("--ngrok-token", help="ngrok API token (or set NGROK_TOKEN env var)")
    generate_parser.add_argument("--codegen-org-id", help="Codegen organization ID (or set CODEGEN_ORG_ID env var)")
    generate_parser.add_argument("--repo-name", help="GitHub repository name (or set REPO_NAME env var)")
    generate_parser.add_argument("--phase", type=int, default=1, help="Phase number (1-based)")
    generate_parser.add_argument("--output-file", help="Path to output file")
    
    args = parser.parse_args()
    
    if args.command == "create":
        return create_requirements_document(args)
    elif args.command == "parse":
        return parse_requirements_document(args)
    elif args.command == "generate":
        return generate_concurrent_queries(args)
    else:
        parser.print_help()
        return 1

if __name__ == "__main__":
    sys.exit(main())
