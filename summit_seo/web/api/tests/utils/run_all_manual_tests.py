#!/usr/bin/env python
"""
Run all manual tests for error handling utilities.
This script runs tests without depending on pytest or settings.
"""
import os
import sys
import unittest

# Add the parent directory to the path
root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../..'))
sys.path.insert(0, root_dir)

# Import test modules
from summit_seo.web.api.tests.utils.test_error_response_manual import TestErrorResponse
from summit_seo.web.api.tests.utils.test_error_handlers_manual import TestErrorHandlers
from summit_seo.web.api.tests.utils.test_middleware_manual import TestErrorHandlingMiddleware

if __name__ == "__main__":
    # Create test loader
    loader = unittest.TestLoader()
    
    # Create test suite
    test_suite = unittest.TestSuite()
    
    # Add tests from each test module
    test_suite.addTests(loader.loadTestsFromTestCase(TestErrorResponse))
    test_suite.addTests(loader.loadTestsFromTestCase(TestErrorHandlers))
    test_suite.addTests(loader.loadTestsFromTestCase(TestErrorHandlingMiddleware))
    
    # Run the test suite
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(test_suite)
    
    # Exit with non-zero code if tests failed
    sys.exit(0 if result.wasSuccessful() else 1) 