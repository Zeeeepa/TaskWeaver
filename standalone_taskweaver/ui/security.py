#!/usr/bin/env python3
"""
Security module for TaskWeaver UI
"""

import os
import secrets
import logging
import time
from typing import Dict, Optional, List, Any, Callable
from functools import wraps

from fastapi import Depends, HTTPException, Request, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("taskweaver-ui-security")

# Security settings
API_KEY_HEADER = "X-API-Key"
API_KEY_ENV_VAR = "TASKWEAVER_API_KEY"
DEFAULT_API_KEY = None  # Will be generated on startup if not provided

# Rate limiting settings
RATE_LIMIT_WINDOW = 60  # seconds
RATE_LIMIT_MAX_REQUESTS = 100  # requests per window
rate_limit_store: Dict[str, List[float]] = {}  # IP -> list of request timestamps

# Bearer token security
security = HTTPBearer()

def get_api_key() -> str:
    """
    Get the API key from environment variable or generate a new one
    
    Returns:
        str: API key
    """
    global DEFAULT_API_KEY
    
    # Check if API key is already set
    if DEFAULT_API_KEY:
        return DEFAULT_API_KEY
    
    # Try to get API key from environment variable
    api_key = os.environ.get(API_KEY_ENV_VAR)
    
    # If not set, generate a new one
    if not api_key:
        api_key = secrets.token_urlsafe(32)
        logger.warning(f"No API key found in environment variable {API_KEY_ENV_VAR}. Generated a new one: {api_key}")
        logger.warning(f"Set this API key in your environment to use it consistently across restarts.")
    else:
        logger.info(f"Using API key from environment variable {API_KEY_ENV_VAR}")
    
    DEFAULT_API_KEY = api_key
    return api_key

def verify_api_key(request: Request) -> bool:
    """
    Verify the API key in the request
    
    Args:
        request: FastAPI request
        
    Returns:
        bool: True if API key is valid, False otherwise
    """
    # Get API key from header
    api_key = request.headers.get(API_KEY_HEADER)
    
    # If no API key provided, check for bearer token
    if not api_key:
        auth_header = request.headers.get("Authorization")
        if auth_header and auth_header.startswith("Bearer "):
            api_key = auth_header.replace("Bearer ", "")
    
    # Verify API key
    return api_key == get_api_key()

def check_rate_limit(request: Request) -> bool:
    """
    Check if the request exceeds the rate limit
    
    Args:
        request: FastAPI request
        
    Returns:
        bool: True if rate limit is not exceeded, False otherwise
    """
    # Get client IP
    client_ip = request.client.host if request.client else "unknown"
    
    # Get current time
    current_time = time.time()
    
    # Initialize rate limit store for this IP if not exists
    if client_ip not in rate_limit_store:
        rate_limit_store[client_ip] = []
    
    # Remove old timestamps
    rate_limit_store[client_ip] = [
        ts for ts in rate_limit_store[client_ip]
        if current_time - ts < RATE_LIMIT_WINDOW
    ]
    
    # Check if rate limit is exceeded
    if len(rate_limit_store[client_ip]) >= RATE_LIMIT_MAX_REQUESTS:
        logger.warning(f"Rate limit exceeded for IP {client_ip}")
        return False
    
    # Add current timestamp
    rate_limit_store[client_ip].append(current_time)
    
    return True

def api_key_auth(request: Request):
    """
    Dependency for API key authentication
    
    Args:
        request: FastAPI request
        
    Raises:
        HTTPException: If API key is invalid or rate limit is exceeded
    """
    # Check rate limit
    if not check_rate_limit(request):
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Rate limit exceeded"
        )
    
    # Verify API key
    if not verify_api_key(request):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API key"
        )
    
    return True

def bearer_auth(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """
    Dependency for bearer token authentication
    
    Args:
        credentials: Bearer token credentials
        
    Raises:
        HTTPException: If token is invalid
    """
    if credentials.credentials != get_api_key():
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials"
        )
    
    return True

def require_auth(func: Callable) -> Callable:
    """
    Decorator for requiring authentication
    
    Args:
        func: Function to decorate
        
    Returns:
        Callable: Decorated function
    """
    @wraps(func)
    async def wrapper(*args, **kwargs):
        request = kwargs.get("request")
        if not request:
            for arg in args:
                if isinstance(arg, Request):
                    request = arg
                    break
        
        if not request:
            raise ValueError("Request object not found in function arguments")
        
        # Check rate limit
        if not check_rate_limit(request):
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="Rate limit exceeded"
            )
        
        # Verify API key
        if not verify_api_key(request):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid API key"
            )
        
        return await func(*args, **kwargs)
    
    return wrapper

