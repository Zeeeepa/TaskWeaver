import json
import os
import re
from pathlib import Path

def get_package_version():
    """Get the package version from version.json."""
    root_dir = Path(__file__).parent.parent
    version_file = root_dir / "version.json"
    
    if not version_file.exists():
        return "0.0.1"  # Default version if file doesn't exist
    
    with open(version_file, "r") as f:
        version_data = json.load(f)
    
    # Use prod version as the base
    version = version_data.get("prod", "0.0.1")
    
    # Add main version if available
    main_version = version_data.get("main", "")
    if main_version:
        version = f"{version}.{main_version}"
    
    # Add dev version if available
    dev_version = version_data.get("dev", "")
    if dev_version:
        version = f"{version}.{dev_version}"
    
    return version

if __name__ == "__main__":
    print(get_package_version())

