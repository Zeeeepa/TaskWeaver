#!/usr/bin/env python3
"""
Bidirectional context sharing between TaskWeaver and Codegen.
"""

from typing import Dict, Any, Optional, List


class BidirectionalContext:
    """
    Bidirectional context sharing between TaskWeaver and Codegen.
    """

    def __init__(self):
        """
        Initialize the bidirectional context.
        """
        self.context = {}
        self.initialized = False

    def initialize(self) -> None:
        """
        Initialize the bidirectional context.
        """
        self.initialized = True

    def set_context(self, key: str, value: Any) -> None:
        """
        Set a context value.

        Args:
            key: The context key.
            value: The context value.
        """
        if not self.initialized:
            self.initialize()
        
        self.context[key] = value

    def get_context(self, key: str, default: Any = None) -> Any:
        """
        Get a context value.

        Args:
            key: The context key.
            default: The default value to return if the key is not found.

        Returns:
            The context value.
        """
        if not self.initialized:
            self.initialize()
        
        return self.context.get(key, default)

    def update_context(self, context: Dict[str, Any]) -> None:
        """
        Update the context with a dictionary.

        Args:
            context: The context dictionary to update with.
        """
        if not self.initialized:
            self.initialize()
        
        self.context.update(context)

    def clear_context(self) -> None:
        """
        Clear the context.
        """
        if not self.initialized:
            self.initialize()
        
        self.context.clear()

    def get_all_context(self) -> Dict[str, Any]:
        """
        Get all context.

        Returns:
            The entire context dictionary.
        """
        if not self.initialized:
            self.initialize()
        
        return self.context.copy()

