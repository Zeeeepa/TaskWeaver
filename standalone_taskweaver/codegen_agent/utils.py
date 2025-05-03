#!/usr/bin/env python3
"""
Utility functions for the Codegen agent integration

This module provides common utility functions used across the Codegen agent integration.
"""

import os
import sys
import json
import logging
import time
from typing import Dict, List, Optional, Any, Union, Tuple, Set

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("codegen-agent-utils")

def initialize_codegen_client(token: str, org_id: Optional[str] = None) -> Any:
    """
    Initialize the Codegen client with the provided token and organization ID
    
    Args:
        token: Codegen API token
        org_id: Optional organization ID
        
    Returns:
        Any: Initialized Codegen client or None if initialization fails
    """
    try:
        # Import here to avoid circular imports
        from codegen import Agent
        
        # Initialize the Codegen agent
        agent = Agent(
            token=token,
            org_id=org_id
        )
        
        logger.info("Codegen agent initialized successfully")
        return agent
    except Exception as e:
        logger.error(f"Failed to initialize Codegen agent: {str(e)}", exc_info=True)
        return None

def safe_execute(func, *args, default_return=None, log_error=True, **kwargs):
    """
    Safely execute a function and handle exceptions
    
    Args:
        func: Function to execute
        *args: Arguments to pass to the function
        default_return: Default return value if the function fails
        log_error: Whether to log the error
        **kwargs: Keyword arguments to pass to the function
        
    Returns:
        Any: Result of the function or default_return if the function fails
    """
    try:
        return func(*args, **kwargs)
    except Exception as e:
        if log_error:
            logger.error(f"Error executing {func.__name__}: {str(e)}", exc_info=True)
        return default_return

def validate_required_params(params: Dict[str, Any], required_params: List[str]) -> Tuple[bool, Optional[str]]:
    """
    Validate that all required parameters are present and not None or empty
    
    Args:
        params: Dictionary of parameters
        required_params: List of required parameter names
        
    Returns:
        Tuple[bool, Optional[str]]: (True, None) if all required parameters are present,
                                   (False, error_message) otherwise
    """
    for param in required_params:
        if param not in params or params[param] is None:
            return False, f"Missing required parameter: {param}"
        
        # Check if the parameter is a string and empty
        if isinstance(params[param], str) and not params[param].strip():
            return False, f"Required parameter {param} cannot be empty"
    
    return True, None

def compress_context(context: Dict[str, Any], max_size: int = 10000) -> Dict[str, Any]:
    """
    Compress a context dictionary to ensure it doesn't exceed a maximum size
    
    Args:
        context: Context dictionary to compress
        max_size: Maximum size of the context in characters
        
    Returns:
        Dict[str, Any]: Compressed context
    """
    # Convert to JSON string to measure size
    context_str = json.dumps(context)
    
    # If the context is already small enough, return it as is
    if len(context_str) <= max_size:
        return context
    
    # Create a compressed version of the context
    compressed_context = {}
    
    # Add essential fields first
    for key in ["project", "requirements", "task"]:
        if key in context:
            compressed_context[key] = context[key]
    
    # Add other fields until we reach the maximum size
    for key, value in context.items():
        if key not in compressed_context:
            # Try adding this field
            temp_context = compressed_context.copy()
            temp_context[key] = value
            
            # Check if adding this field would exceed the maximum size
            if len(json.dumps(temp_context)) <= max_size:
                compressed_context[key] = value
    
    # If we still exceed the maximum size, truncate the context
    compressed_str = json.dumps(compressed_context)
    if len(compressed_str) > max_size:
        logger.warning(f"Context size ({len(compressed_str)}) exceeds maximum size ({max_size}). Truncating context.")
        return {"warning": "Context was truncated due to size constraints", "truncated_context": compressed_context}
    
    return compressed_context

