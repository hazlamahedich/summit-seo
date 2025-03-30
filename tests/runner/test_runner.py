"""
Test runner to execute specific test modules individually.
This helps isolate and fix circular import issues.
"""

import os
import sys
import importlib.util
import pytest
import asyncio

def run_test_file(test_file_path):
    """
    Run a specific test file using pytest.
    
    Args:
        test_file_path: Path to the test file to run
    """
    print(f"Running tests from: {test_file_path}")
    exit_code = pytest.main(["-v", test_file_path])
    return exit_code

def import_test_file(test_file_path):
    """
    Import a test file as a module to check for import errors.
    
    Args:
        test_file_path: Path to the test file to import
    """
    module_name = os.path.basename(test_file_path).replace(".py", "")
    spec = importlib.util.spec_from_file_location(module_name, test_file_path)
    module = importlib.util.module_from_spec(spec)
    
    try:
        spec.loader.exec_module(module)
        print(f"Successfully imported {module_name}")
        return True
    except Exception as e:
        print(f"Failed to import {module_name}: {e}")
        return False

def test_parallel_executor():
    """Test the parallel executor implementation."""
    test_file = "tests/parallel/test_executor.py"
    if import_test_file(test_file):
        return run_test_file(test_file)
    return 1

def test_task():
    """Test the task and task group implementations."""
    test_file = "tests/parallel/test_task.py"
    if import_test_file(test_file):
        return run_test_file(test_file)
    return 1

def test_memory_limiter():
    """Test the memory limiter implementation."""
    test_file = "tests/memory/test_memory_limiter.py"
    if import_test_file(test_file):
        return run_test_file(test_file)
    return 1

def test_memory_optimizer():
    """Test the memory optimizer implementation."""
    test_file = "tests/memory/test_memory_optimizer.py"
    if import_test_file(test_file):
        return run_test_file(test_file)
    return 1

def test_integration():
    """Test the integration between memory optimization and parallel processing."""
    test_file = "tests/integration/test_memory_parallel_integration.py"
    if import_test_file(test_file):
        return run_test_file(test_file)
    return 1

def run_all_tests():
    """Run all test modules."""
    results = {
        "parallel_executor": test_parallel_executor(),
        "task": test_task(),
        "memory_limiter": test_memory_limiter(),
        "memory_optimizer": test_memory_optimizer(),
        "integration": test_integration(),
    }
    
    print("\n== Test Results Summary ==")
    success = True
    for name, result in results.items():
        status = "PASSED" if result == 0 else "FAILED"
        print(f"{name}: {status}")
        if result != 0:
            success = False
    
    return 0 if success else 1

if __name__ == "__main__":
    # Configure event loop policy for asyncio tests
    if sys.platform == 'win32' and hasattr(asyncio, 'WindowsSelectorEventLoopPolicy'):
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    
    # Process command line args to determine which tests to run
    if len(sys.argv) > 1:
        test_name = sys.argv[1]
        if test_name == "executor":
            sys.exit(test_parallel_executor())
        elif test_name == "task":
            sys.exit(test_task())
        elif test_name == "limiter":
            sys.exit(test_memory_limiter())
        elif test_name == "optimizer":
            sys.exit(test_memory_optimizer())
        elif test_name == "integration":
            sys.exit(test_integration())
        else:
            print(f"Unknown test: {test_name}")
            print("Available tests: executor, task, limiter, optimizer, integration")
            sys.exit(1)
    else:
        # Run all tests by default
        sys.exit(run_all_tests()) 