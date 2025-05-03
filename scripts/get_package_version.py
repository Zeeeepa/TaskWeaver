#!/usr/bin/env python3
"""
Get the package version from git tags or environment variables.
"""

import os
import subprocess
import re
from datetime import datetime


def get_package_version() -> str:
    """
    Get the package version from git tags or environment variables.
    
    Returns:
        str: The package version
    """
    # Check if version is set in environment variable
    if "TASKWEAVER_VERSION" in os.environ:
        return os.environ["TASKWEAVER_VERSION"]
    
    # Try to get version from git tags
    try:
        # Get the latest tag
        result = subprocess.run(
            ["git", "describe", "--tags", "--abbrev=0"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False,
            text=True,
        )
        
        if result.returncode == 0:
            tag = result.stdout.strip()
            # Remove 'v' prefix if present
            if tag.startswith("v"):
                tag = tag[1:]
            return tag
    except Exception:
        pass
    
    # If no tag found, use date-based version
    now = datetime.now()
    return f"0.1.0.dev{now.strftime('%Y%m%d')}"


if __name__ == "__main__":
    print(get_package_version())

