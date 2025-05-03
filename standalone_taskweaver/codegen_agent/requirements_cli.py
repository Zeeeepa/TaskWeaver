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

def create_requirements_document(args):
    """
    Create a requirements document
    """
    # Initialize the app
    app = TaskWeaverApp()
    config = AppConfigSource()
    logger = TelemetryLogger()
    
    # Initialize the integration
    integration = CodegenIntegration(app, config, logger)
    success = integration.initialize(
        github_token=args.github_token,
        codegen_token=args.codegen_token,
        ngrok_token=args.ngrok_token,
        codegen_org_id=args.codegen_org_id,
        repo_name=args.repo_name
    )
    
    if not success:
        logger.error("Failed to initialize Codegen integration")
        return 1
    
    # Initialize the requirements manager
    requirements_manager = RequirementsManager(app, config, logger, integration)
    
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
    # Initialize the app
    app = TaskWeaverApp()
    config = AppConfigSource()
    logger = TelemetryLogger()
    
    # Initialize the integration
    integration = CodegenIntegration(app, config, logger)
    success = integration.initialize(
        github_token=args.github_token,
        codegen_token=args.codegen_token,
        ngrok_token=args.ngrok_token,
        codegen_org_id=args.codegen_org_id,
        repo_name=args.repo_name
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
    # Initialize the app
    app = TaskWeaverApp()
    config = AppConfigSource()
    logger = TelemetryLogger()
    
    # Initialize the integration
    integration = CodegenIntegration(app, config, logger)
    success = integration.initialize(
        github_token=args.github_token,
        codegen_token=args.codegen_token,
        ngrok_token=args.ngrok_token,
        codegen_org_id=args.codegen_org_id,
        repo_name=args.repo_name
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
    create_parser.add_argument("--github-token", required=True, help="GitHub API token")
    create_parser.add_argument("--codegen-token", required=True, help="Codegen API token")
    create_parser.add_argument("--ngrok-token", required=True, help="ngrok API token")
    create_parser.add_argument("--codegen-org-id", required=True, help="Codegen organization ID")
    create_parser.add_argument("--repo-name", required=True, help="GitHub repository name")
    create_parser.add_argument("--project-name", required=True, help="Project name")
    create_parser.add_argument("--requirements", help="Requirements content")
    create_parser.add_argument("--requirements-file", help="Path to requirements file")
    create_parser.add_argument("--structure-file", help="Path to current structure file")
    create_parser.add_argument("--ui-mockup-file", help="Path to UI mockup file")
    
    # Parse requirements document
    parse_parser = subparsers.add_parser("parse", help="Parse a requirements document")
    parse_parser.add_argument("--github-token", required=True, help="GitHub API token")
    parse_parser.add_argument("--codegen-token", required=True, help="Codegen API token")
    parse_parser.add_argument("--ngrok-token", required=True, help="ngrok API token")
    parse_parser.add_argument("--codegen-org-id", required=True, help="Codegen organization ID")
    parse_parser.add_argument("--repo-name", required=True, help="GitHub repository name")
    parse_parser.add_argument("--output-file", help="Path to output file")
    
    # Generate concurrent queries
    generate_parser = subparsers.add_parser("generate", help="Generate concurrent queries")
    generate_parser.add_argument("--github-token", required=True, help="GitHub API token")
    generate_parser.add_argument("--codegen-token", required=True, help="Codegen API token")
    generate_parser.add_argument("--ngrok-token", required=True, help="ngrok API token")
    generate_parser.add_argument("--codegen-org-id", required=True, help="Codegen organization ID")
    generate_parser.add_argument("--repo-name", required=True, help="GitHub repository name")
    generate_parser.add_argument("--phase", type=int, default=1, help="Phase number (1-based)")
    generate_parser.add_argument("--output-file", help="Path to output file")
    
    args = parser.parse_args()
    
    if args.command == "create":
        if not args.requirements and not args.requirements_file:
            parser.error("Either --requirements or --requirements-file is required")
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

