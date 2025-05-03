#!/usr/bin/env python3
"""
Configuration module for TaskWeaver-Codegen Integration

This module provides configuration classes for the integration.
"""

import os
import logging
from typing import Dict, List, Optional, Any

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("configuration")

class Configuration:
    """
    Configuration class for Codegen integration
    """
    
    def __init__(self) -> None:
        self.github_token = None
        self.codegen_token = None
        self.ngrok_token = None
        self.codegen_org_id = None
        self.repo_name = None
        self.api_base_url = "https://api.codegen.sh"
        self.github_api_base_url = "https://api.github.com"
        self.ngrok_api_base_url = "https://api.ngrok.com"
        self.timeout = 60  # seconds
        
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "github_token": self.github_token,
            "codegen_token": self.codegen_token,
            "ngrok_token": self.ngrok_token,
            "codegen_org_id": self.codegen_org_id,
            "repo_name": self.repo_name,
            "api_base_url": self.api_base_url,
            "github_api_base_url": self.github_api_base_url,
            "ngrok_api_base_url": self.ngrok_api_base_url,
            "timeout": self.timeout,
        }
        
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Configuration':
        """Create from dictionary"""
        config = cls()
        config.github_token = data.get("github_token")
        config.codegen_token = data.get("codegen_token")
        config.ngrok_token = data.get("ngrok_token")
        config.codegen_org_id = data.get("codegen_org_id")
        config.repo_name = data.get("repo_name")
        config.api_base_url = data.get("api_base_url", "https://api.codegen.sh")
        config.github_api_base_url = data.get("github_api_base_url", "https://api.github.com")
        config.ngrok_api_base_url = data.get("ngrok_api_base_url", "https://api.ngrok.com")
        config.timeout = data.get("timeout", 60)
        return config
        
    def validate(self) -> bool:
        """Validate configuration"""
        if not self.github_token:
            logger.error("GitHub token is required")
            return False
            
        if not self.codegen_token:
            logger.error("Codegen token is required")
            return False
            
        if not self.ngrok_token:
            logger.error("ngrok token is required")
            return False
            
        if not self.codegen_org_id:
            logger.error("Codegen organization ID is required")
            return False
            
        return True

