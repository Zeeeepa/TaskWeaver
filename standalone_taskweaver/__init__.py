"""
TaskWeaver is a code-first agent framework for seamlessly planning and executing data analytics tasks.

This module contains the core functionality of TaskWeaver.
"""

from standalone_taskweaver.app import TaskWeaverApp, SessionManager
from standalone_taskweaver.config import AppConfigSource
from standalone_taskweaver.session import Session
from standalone_taskweaver.version import __version__

__all__ = ["TaskWeaverApp", "SessionManager", "AppConfigSource", "Session", "__version__"]
