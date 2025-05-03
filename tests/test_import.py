#!/usr/bin/env python3
"""
Basic import test for TaskWeaver.
"""

def test_import_taskweaver():
    """Test that TaskWeaver can be imported."""
    import taskweaver
    assert taskweaver is not None

def test_import_standalone_taskweaver():
    """Test that standalone_taskweaver can be imported."""
    import standalone_taskweaver
    assert standalone_taskweaver is not None

def test_import_app():
    """Test that the app module can be imported."""
    from standalone_taskweaver.app import app
    assert app is not None

