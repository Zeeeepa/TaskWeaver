"""
Basic tests for the TaskWeaver package structure.
"""

import importlib.util
import os
import sys


def test_package_importable():
    """Test that the taskweaver package can be imported."""
    try:
        import taskweaver
        assert hasattr(taskweaver, "__version__")
        assert hasattr(taskweaver, "TaskWeaverApp")
    except ImportError:
        assert False, "Failed to import taskweaver package"


def test_main_module_exists():
    """Test that the __main__.py module exists and is importable."""
    try:
        from taskweaver import __main__
        assert hasattr(__main__, "main")
    except ImportError:
        assert False, "Failed to import __main__ module"


def test_py_typed_exists():
    """Test that the py.typed file exists."""
    try:
        import taskweaver
        package_dir = os.path.dirname(taskweaver.__file__)
        py_typed_path = os.path.join(package_dir, "py.typed")
        assert os.path.exists(py_typed_path), "py.typed file not found"
    except ImportError:
        assert False, "Failed to import taskweaver package"

