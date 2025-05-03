#!/usr/bin/env python3
"""
Requirements Manager Module

This module provides functionality for managing requirements in TaskWeaver.
"""

import os
import sys
import json
import logging
import re
from typing import Dict, List, Optional, Any, Union, Tuple

from injector import inject

from standalone_taskweaver.app.app import TaskWeaverApp
from standalone_taskweaver.config.config_mgt import AppConfigSource
from standalone_taskweaver.logging import TelemetryLogger

class RequirementsManager:
    """
    Manager for requirements in TaskWeaver
    """
    
    @inject
    def __init__(
        self,
        app: TaskWeaverApp,
        config: AppConfigSource,
        logger: TelemetryLogger,
    ) -> None:
        self.app = app
        self.config = config
        self.logger = logger
        self.requirements = []
        
    def parse_requirements(self, requirements_text: str) -> List[Dict[str, Any]]:
        """
        Parse requirements from text
        
        Args:
            requirements_text: Requirements text
            
        Returns:
            List[Dict[str, Any]]: List of parsed requirements
        """
        try:
            # Split the text into lines
            lines = requirements_text.strip().split("\n")
            
            # Parse requirements
            parsed_requirements = []
            current_requirement = None
            
            for line in lines:
                line = line.strip()
                
                # Skip empty lines
                if not line:
                    continue
                    
                # Check if the line is a requirement
                if line.startswith("- ") or line.startswith("* "):
                    # If there's a current requirement, add it to the list
                    if current_requirement:
                        parsed_requirements.append(current_requirement)
                        
                    # Create a new requirement
                    current_requirement = {
                        "text": line[2:].strip(),
                        "description": "",
                        "priority": "medium",
                        "status": "pending"
                    }
                    
                    # Check for priority markers
                    if "[high]" in line.lower():
                        current_requirement["priority"] = "high"
                        current_requirement["text"] = current_requirement["text"].replace("[high]", "").strip()
                    elif "[medium]" in line.lower():
                        current_requirement["priority"] = "medium"
                        current_requirement["text"] = current_requirement["text"].replace("[medium]", "").strip()
                    elif "[low]" in line.lower():
                        current_requirement["priority"] = "low"
                        current_requirement["text"] = current_requirement["text"].replace("[low]", "").strip()
                        
                    # Check for status markers
                    if "[done]" in line.lower():
                        current_requirement["status"] = "done"
                        current_requirement["text"] = current_requirement["text"].replace("[done]", "").strip()
                    elif "[in progress]" in line.lower():
                        current_requirement["status"] = "in progress"
                        current_requirement["text"] = current_requirement["text"].replace("[in progress]", "").strip()
                    elif "[pending]" in line.lower():
                        current_requirement["status"] = "pending"
                        current_requirement["text"] = current_requirement["text"].replace("[pending]", "").strip()
                elif current_requirement:
                    # Add the line to the description of the current requirement
                    current_requirement["description"] += line + "\n"
                    
            # Add the last requirement
            if current_requirement:
                parsed_requirements.append(current_requirement)
                
            # Store the parsed requirements
            self.requirements = parsed_requirements
            
            return parsed_requirements
        except Exception as e:
            self.logger.error(f"Error parsing requirements: {str(e)}")
            return []
            
    def generate_requirements_markdown(self, requirements: List[Dict[str, Any]]) -> str:
        """
        Generate Markdown text from requirements
        
        Args:
            requirements: List of requirements
            
        Returns:
            str: Markdown text
        """
        try:
            # Generate Markdown text
            markdown = "# Requirements\n\n"
            
            # Add requirements
            for requirement in requirements:
                # Add priority and status markers
                markers = []
                
                if requirement.get("priority") != "medium":
                    markers.append(f"[{requirement.get('priority')}]")
                    
                if requirement.get("status") != "pending":
                    markers.append(f"[{requirement.get('status')}]")
                    
                markers_text = " ".join(markers)
                
                if markers_text:
                    markdown += f"- {requirement.get('text')} {markers_text}\n"
                else:
                    markdown += f"- {requirement.get('text')}\n"
                    
                # Add description
                description = requirement.get("description", "").strip()
                if description:
                    # Indent the description
                    indented_description = "\n".join([f"  {line}" for line in description.split("\n")])
                    markdown += f"{indented_description}\n"
                    
                markdown += "\n"
                
            return markdown
        except Exception as e:
            self.logger.error(f"Error generating requirements Markdown: {str(e)}")
            return ""
            
    def update_requirement_status(self, requirement_text: str, status: str) -> bool:
        """
        Update the status of a requirement
        
        Args:
            requirement_text: Text of the requirement
            status: New status
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            # Find the requirement
            for requirement in self.requirements:
                if requirement.get("text") == requirement_text:
                    # Update the status
                    requirement["status"] = status
                    return True
                    
            return False
        except Exception as e:
            self.logger.error(f"Error updating requirement status: {str(e)}")
            return False
            
    def get_pending_requirements(self) -> List[Dict[str, Any]]:
        """
        Get pending requirements
        
        Returns:
            List[Dict[str, Any]]: List of pending requirements
        """
        try:
            # Filter requirements by status
            return [req for req in self.requirements if req.get("status") == "pending"]
        except Exception as e:
            self.logger.error(f"Error getting pending requirements: {str(e)}")
            return []
            
    def get_in_progress_requirements(self) -> List[Dict[str, Any]]:
        """
        Get in-progress requirements
        
        Returns:
            List[Dict[str, Any]]: List of in-progress requirements
        """
        try:
            # Filter requirements by status
            return [req for req in self.requirements if req.get("status") == "in progress"]
        except Exception as e:
            self.logger.error(f"Error getting in-progress requirements: {str(e)}")
            return []
            
    def get_completed_requirements(self) -> List[Dict[str, Any]]:
        """
        Get completed requirements
        
        Returns:
            List[Dict[str, Any]]: List of completed requirements
        """
        try:
            # Filter requirements by status
            return [req for req in self.requirements if req.get("status") == "done"]
        except Exception as e:
            self.logger.error(f"Error getting completed requirements: {str(e)}")
            return []

