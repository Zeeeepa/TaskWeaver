#!/usr/bin/env python3
"""
Task Polling Utilities

This module provides helper functions for polling Codegen tasks until they reach
a terminal state, with both synchronous and asynchronous implementations.
"""

import time
import asyncio
import logging
from typing import List, Set, Optional, Any, Dict

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("task-polling")

# Terminal states for Codegen tasks
TERMINAL_STATES = ["completed", "failed", "cancelled"]

async def poll_codegen_task_async(codegen_task, poll_interval=5):
    """
    Poll a Codegen task asynchronously until it reaches a terminal state.
    
    Args:
        codegen_task: The Codegen task to poll
        poll_interval: Interval in seconds between polling attempts
        
    Returns:
        The Codegen task after it has reached a terminal state
    """
    while codegen_task.status not in TERMINAL_STATES:
        codegen_task.refresh()
        await asyncio.sleep(poll_interval)
    return codegen_task

def poll_codegen_task_sync(codegen_task, poll_interval=5, max_retries=30):
    """
    Poll a Codegen task synchronously until it reaches a terminal state.
    
    Args:
        codegen_task: The Codegen task to poll
        poll_interval: Interval in seconds between polling attempts
        max_retries: Maximum number of polling attempts
        
    Returns:
        The Codegen task after it has reached a terminal state
    """
    for _ in range(max_retries):
        codegen_task.refresh()
        if codegen_task.status in TERMINAL_STATES:
            break
        time.sleep(poll_interval)
    return codegen_task

