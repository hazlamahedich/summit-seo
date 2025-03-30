import pytest

"""
Basic tests to verify the project setup is working.
"""

def test_basic():
    """Basic test to verify pytest is working."""
    assert True

def test_import():
    """Test that we can import our package."""
    try:
        from summit_seo import __version__
        assert isinstance(__version__, str)
    except ImportError as e:
        pytest.fail(f"Failed to import package: {e}") 