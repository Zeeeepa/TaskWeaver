#!/usr/bin/env python3
"""
Utility functions for the Codegen agent integration

This module provides common utility functions used across the Codegen agent integration.
These utilities help with client initialization, error handling, parameter validation,
and context management to ensure consistent behavior across the codebase.
"""

import os
import sys
import json
import logging
import time
import traceback
from typing import Dict, List, Optional, Any, Union, Tuple, Set, Callable, TypeVar

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("codegen-agent-utils")

# Type variable for generic function return type
T = TypeVar('T')

def initialize_codegen_client(token: str, org_id: Optional[str] = None) -> Any:
    """
    Initialize the Codegen client with the provided token and organization ID
    
    Args:
        token: Codegen API token
        org_id: Optional organization ID
        
    Returns:
        Any: Initialized Codegen client or None if initialization fails
        
    Example:
        ```python
        agent = initialize_codegen_client("your-token-here")
        if agent:
            # Use the agent
            result = agent.execute_task(...)
        else:
            # Handle initialization failure
            logger.error("Failed to initialize Codegen agent")
        ```
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
    except ImportError as e:
        logger.error(f"Failed to import Codegen SDK: {str(e)}. Make sure it's installed.", exc_info=True)
        return None
    except Exception as e:
        logger.error(f"Failed to initialize Codegen agent: {str(e)}", exc_info=True)
        return None

def safe_execute(func: Callable[..., T], *args, default_return: Optional[T] = None, 
                log_error: bool = True, reraise: bool = False, **kwargs) -> Optional[T]:
    """
    Safely execute a function and handle exceptions
    
    Args:
        func: Function to execute
        *args: Arguments to pass to the function
        default_return: Default return value if the function fails
        log_error: Whether to log the error
        reraise: Whether to re-raise the exception after logging
        **kwargs: Keyword arguments to pass to the function
        
    Returns:
        Any: Result of the function or default_return if the function fails
        
    Example:
        ```python
        # Simple usage with default return value
        result = safe_execute(some_function, arg1, arg2, default_return=None)
        
        # Re-raising exceptions after logging
        try:
            result = safe_execute(some_function, arg1, arg2, reraise=True)
        except Exception as e:
            # Handle the exception
            pass
        ```
    """
    try:
        return func(*args, **kwargs)
    except Exception as e:
        if log_error:
            logger.error(f"Error executing {func.__name__}: {str(e)}", exc_info=True)
        if reraise:
            raise
        return default_return

def validate_required_params(params: Dict[str, Any], required_params: List[str], 
                           type_checks: Optional[Dict[str, type]] = None) -> Tuple[bool, Optional[str]]:
    """
    Validate that all required parameters are present, not None or empty,
    and optionally check their types
    
    Args:
        params: Dictionary of parameters
        required_params: List of required parameter names
        type_checks: Optional dictionary mapping parameter names to expected types
        
    Returns:
        Tuple[bool, Optional[str]]: (True, None) if all required parameters are present and valid,
                                   (False, error_message) otherwise
                                   
    Example:
        ```python
        # Basic validation
        valid, error_msg = validate_required_params(
            {"name": "John", "age": 30},
            ["name", "age"]
        )
        
        # With type checking
        valid, error_msg = validate_required_params(
            {"name": "John", "age": 30},
            ["name", "age"],
            {"name": str, "age": int}
        )
        
        if not valid:
            raise ValueError(error_msg)
        ```
    """
    # Check for missing or None parameters
    for param in required_params:
        if param not in params or params[param] is None:
            return False, f"Missing required parameter: {param}"
        
        # Check if the parameter is a string and empty
        if isinstance(params[param], str) and not params[param].strip():
            return False, f"Required parameter {param} cannot be empty"
    
    # Check parameter types if type_checks is provided
    if type_checks:
        for param, expected_type in type_checks.items():
            if param in params and params[param] is not None:
                if not isinstance(params[param], expected_type):
                    return False, f"Parameter {param} must be of type {expected_type.__name__}, got {type(params[param]).__name__}"
    
    return True, None

def compress_context(context: Dict[str, Any], max_size: int = 10000) -> Dict[str, Any]:
    """
    Compress a context dictionary to ensure it doesn't exceed a maximum size
    
    Args:
        context: Context dictionary to compress
        max_size: Maximum size of the context in characters
        
    Returns:
        Dict[str, Any]: Compressed context
        
    Example:
        ```python
        # Compress a large context
        original_context = {...}  # Large dictionary
        compressed = compress_context(original_context, max_size=5000)
        
        # Check if compression occurred
        if "warning" in compressed:
            logger.warning("Context was compressed due to size constraints")
        ```
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
        return {
            "warning": "Context was truncated due to size constraints", 
            "original_size": len(context_str),
            "compressed_size": len(compressed_str),
            "truncated_context": compressed_context
        }
    
    return compressed_context

def get_memory_usage() -> Dict[str, Any]:
    """
    Get current memory usage information
    
    Returns:
        Dict[str, Any]: Dictionary with memory usage information
        
    Example:
        ```python
        # Get memory usage
        memory_info = get_memory_usage()
        logger.info(f"Current memory usage: {memory_info['current_mb']} MB")
        ```
    """
    try:
        import psutil
        process = psutil.Process(os.getpid())
        memory_info = process.memory_info()
        
        return {
            "current_bytes": memory_info.rss,
            "current_mb": memory_info.rss / (1024 * 1024),
            "percent": process.memory_percent(),
            "timestamp": time.time()
        }
    except ImportError:
        logger.warning("psutil not installed, cannot get detailed memory usage")
        return {
            "timestamp": time.time(),
            "note": "Install psutil for detailed memory information"
        }
    except Exception as e:
        logger.error(f"Error getting memory usage: {str(e)}", exc_info=True)
        return {
            "error": str(e),
            "timestamp": time.time()
        }
