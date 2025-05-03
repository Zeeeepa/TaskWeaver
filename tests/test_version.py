import pytest
from standalone_taskweaver.version import __version__

def test_version():
    """Test that the version is a string and not empty."""
    assert isinstance(__version__, str)
    assert __version__ != ""
    assert __version__ == "0.2.0"

