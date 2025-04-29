"""
Metadata module for TaskWeaver.

This module contains metadata classes used across different modules.
"""

from dataclasses import dataclass


@dataclass
class SessionMetadata:
    """
    SessionMetadata is used to store the metadata of a session.
    """

    session_id: str
    session_name: str
    session_dir: str
    execution_cwd: str

