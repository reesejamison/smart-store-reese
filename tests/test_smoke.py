"""Test that the project structure works correctly.

Module Information:
    - Filename: test_smoke.py
    - Module: test_smoke
    - Location: tests/

This smoke test verifies that:
    - All modules can be imported
    - Basic project structure is intact
"""

from analytics_project import data_prep
from analytics_project import utils_logger


def test_imports_work():
    """Verify all modules can be imported."""
    # If we get here without ImportError, imports work
    assert data_prep is not None
    assert utils_logger is not None


def test_data_prep_functions():
    """Verify data_prep module's basic functionality."""
    # Initialize logger
    utils_logger.init_logger()

    # Test read_and_log function with a sample DataFrame
    import pandas as pd
    test_df = pd.DataFrame({'A': [1, 2], 'B': [3, 4]})

    # Just verify the function exists and can be called
    assert hasattr(data_prep, 'read_and_log')
    assert callable(data_prep.read_and_log)




