"""
TaskWeaver - A code-first agent framework for data analytics tasks
"""

import json
import os
import importlib.metadata
import logging

logger = logging.getLogger(__name__)

# Try to get version from version.json
try:
    version_file = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "version.json")
    if os.path.exists(version_file):
        try:
            with open(version_file, "r") as f:
                version_info = json.load(f)
                __version__ = version_info.get("version", "0.1.0")
        except json.JSONDecodeError as e:
            logger.warning(f"Error parsing version.json: {e}")
            __version__ = "0.1.0"
    else:
        # Try to get version from package metadata
        try:
            __version__ = importlib.metadata.version("taskweaver")
        except importlib.metadata.PackageNotFoundError:
            __version__ = "0.1.0"
except Exception as e:
    logger.warning(f"Error determining version: {e}")
    __version__ = "0.1.0"

__author__ = "Microsoft TaskWeaver"
__email__ = "taskweaver@microsoft.com"
