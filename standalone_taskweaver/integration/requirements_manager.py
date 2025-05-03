#!/usr/bin/env python3
"""
Requirements manager for TaskWeaver.
"""

import os
import re
from typing import Dict, Any, Optional, List, Set


class RequirementsManager:
    """
    Requirements manager for TaskWeaver.
    """

    def __init__(self, requirements_file: Optional[str] = None):
        """
        Initialize the requirements manager.

        Args:
            requirements_file: Optional path to requirements file.
        """
        self.requirements_file = requirements_file or "requirements.txt"
        self.requirements = set()
        self.initialized = False

    def initialize(self) -> None:
        """
        Initialize the requirements manager.
        """
        if os.path.exists(self.requirements_file):
            self.load_requirements()
        
        self.initialized = True

    def load_requirements(self) -> None:
        """
        Load requirements from file.
        """
        with open(self.requirements_file, "r") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#"):
                    self.requirements.add(line)

    def save_requirements(self) -> None:
        """
        Save requirements to file.
        """
        with open(self.requirements_file, "w") as f:
            for req in sorted(self.requirements):
                f.write(f"{req}\n")

    def add_requirement(self, requirement: str) -> None:
        """
        Add a requirement.

        Args:
            requirement: The requirement to add.
        """
        if not self.initialized:
            self.initialize()
        
        self.requirements.add(requirement)

    def remove_requirement(self, requirement: str) -> None:
        """
        Remove a requirement.

        Args:
            requirement: The requirement to remove.
        """
        if not self.initialized:
            self.initialize()
        
        if requirement in self.requirements:
            self.requirements.remove(requirement)

    def get_requirements(self) -> Set[str]:
        """
        Get all requirements.

        Returns:
            The set of requirements.
        """
        if not self.initialized:
            self.initialize()
        
        return self.requirements.copy()

    def parse_requirements_from_text(self, text: str) -> List[str]:
        """
        Parse requirements from text.

        Args:
            text: The text to parse requirements from.

        Returns:
            The list of requirements.
        """
        if not self.initialized:
            self.initialize()
        
        requirements = []
        
        # Match pip install statements
        pip_install_pattern = r"pip\s+install\s+([\w\-\.\[\]>=<]+)"
        pip_installs = re.findall(pip_install_pattern, text)
        requirements.extend(pip_installs)
        
        # Match import statements
        import_pattern = r"import\s+([\w\-\.]+)"
        imports = re.findall(import_pattern, text)
        requirements.extend(imports)
        
        # Match from ... import statements
        from_import_pattern = r"from\s+([\w\-\.]+)\s+import"
        from_imports = re.findall(from_import_pattern, text)
        requirements.extend(from_imports)
        
        # Clean up requirements
        cleaned_requirements = []
        for req in requirements:
            # Remove version specifiers
            req = re.sub(r"[>=<\[\]]+.*$", "", req)
            # Remove submodules
            req = req.split(".")[0]
            # Skip standard library modules
            if req not in ["os", "sys", "re", "math", "json", "time", "datetime", "random", "collections", "itertools"]:
                cleaned_requirements.append(req)
        
        return cleaned_requirements

    def add_requirements_from_text(self, text: str) -> None:
        """
        Add requirements from text.

        Args:
            text: The text to parse requirements from.
        """
        if not self.initialized:
            self.initialize()
        
        requirements = self.parse_requirements_from_text(text)
        for req in requirements:
            self.add_requirement(req)

