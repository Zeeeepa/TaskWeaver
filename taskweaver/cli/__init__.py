"""
TaskWeaver CLI Module
"""

import logging
import os
from typing import Optional

logger = logging.getLogger(__name__)


def run_cli(project_dir: str, interactive: bool = False, config_path: Optional[str] = None):
    """
    Run the TaskWeaver CLI
    
    Args:
        project_dir: Project directory path
        interactive: Whether to run in interactive mode
        config_path: Path to configuration file
        
    Returns:
        int: Exit code
    """
    try:
        # Validate project directory
        if not os.path.exists(project_dir):
            logger.error(f"Project directory not found: {project_dir}")
            return 1
        
        # Apply configuration if provided
        if config_path:
            if not os.path.exists(config_path):
                logger.error(f"Configuration file not found: {config_path}")
                return 1
            os.environ["TASKWEAVER_CONFIG_PATH"] = config_path
            logger.info(f"Using configuration from {config_path}")
        
        # Run in interactive mode if requested
        if interactive:
            logger.info(f"Running in interactive mode with project directory: {project_dir}")
            # TODO: Implement interactive mode
            print("Interactive mode not yet implemented")
            return 0
        else:
            # Initialize and return
            logger.info(f"Initializing project directory: {project_dir}")
            # TODO: Implement initialization
            print(f"Project directory initialized: {project_dir}")
            return 0
    except Exception as e:
        logger.error(f"Error running CLI: {str(e)}")
        return 1

