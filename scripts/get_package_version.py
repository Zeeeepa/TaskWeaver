#!/usr/bin/env python3
"""
Script to get the package version from version.json
"""

import json
import os


def get_package_version():
    """
    Get the package version from version.json
    """
    version_file = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "version.json")
    
    if not os.path.exists(version_file):
        return "0.1.0"  # Default version if version.json doesn't exist
    
    with open(version_file, "r") as f:
        version_info = json.load(f)
        return version_info.get("version", "0.1.0")


if __name__ == "__main__":
    print(get_package_version())

