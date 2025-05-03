"""
Basic tests for the TaskWeaver package structure.
"""

import importlib.util
import os
import sys


def test_package_importable():
    """
    Test that the taskweaver package can be imported.
    
    This test verifies that:
    1. The package can be imported without errors
    2. The package has a __version__ attribute (required for proper versioning)
    3. The package exposes the TaskWeaverApp class (main entry point for users)
    """
    try:
        import taskweaver
        assert hasattr(taskweaver, "__version__")
        assert hasattr(taskweaver, "TaskWeaverApp")
    except ImportError:
        assert False, "Failed to import taskweaver package"


def test_main_module_exists():
    """
    Test that the __main__.py module exists and is importable.
    
    This ensures that the package can be executed using:
    python -m taskweaver
    """
    try:
        from taskweaver import __main__
        assert hasattr(__main__, "main")
    except ImportError:
        assert False, "Failed to import __main__ module"


def test_py_typed_exists():
    """
    Test that the py.typed file exists.
    
    This file is required for PEP 561 type hint support.
    Its presence indicates that the package's type annotations should be
    used by type checking tools.
    """
    try:
        import taskweaver
        package_dir = os.path.dirname(taskweaver.__file__)
        py_typed_path = os.path.join(package_dir, "py.typed")
        assert os.path.exists(py_typed_path), "py.typed file not found"
    except ImportError:
        assert False, "Failed to import taskweaver package"
