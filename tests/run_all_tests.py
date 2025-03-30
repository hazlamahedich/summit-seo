#!/usr/bin/env python
"""
Automated test runner for Summit SEO project.

This script runs all tests with coverage and generates coverage reports.
It can also be used to run specific test modules or test cases.
"""

import os
import sys
import argparse
import subprocess
import shutil
from datetime import datetime

# Default directories and files
TEST_DIR = "tests"
COVERAGE_DIR = "coverage_reports"
COVERAGE_DATA_FILE = ".coverage"
PROJECT_PACKAGES = ["summit_seo"]

def parse_arguments():
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(description="Run Summit SEO tests with options")
    
    parser.add_argument(
        "-m", "--module", 
        help="Run tests for a specific module (e.g., analyzer, processor)"
    )
    
    parser.add_argument(
        "-t", "--test", 
        help="Run a specific test file or test case (e.g., test_content_analyzer)"
    )
    
    parser.add_argument(
        "-k", "--keyword", 
        help="Only run tests which match the given substring expression"
    )
    
    parser.add_argument(
        "-v", "--verbose", 
        action="store_true", 
        help="Increase verbosity of the output"
    )
    
    parser.add_argument(
        "--no-coverage", 
        action="store_true", 
        help="Run tests without coverage"
    )
    
    parser.add_argument(
        "--html-report", 
        action="store_true", 
        help="Generate HTML coverage report"
    )
    
    parser.add_argument(
        "--xml-report", 
        action="store_true", 
        help="Generate XML coverage report for CI integration"
    )
    
    parser.add_argument(
        "--fail-under", 
        type=int, 
        default=80, 
        help="Fail if coverage percentage is under given threshold (default: 80)"
    )
    
    return parser.parse_args()

def prepare_environment():
    """Prepare the test environment."""
    # Create coverage directory if it doesn't exist
    if not os.path.exists(COVERAGE_DIR):
        os.makedirs(COVERAGE_DIR)
    
    # Remove old coverage data
    if os.path.exists(COVERAGE_DATA_FILE):
        os.remove(COVERAGE_DATA_FILE)

def build_pytest_command(args):
    """Build the pytest command based on arguments."""
    cmd = ["python", "-m", "pytest"]
    
    # Add verbosity
    if args.verbose:
        cmd.append("-v")
    
    # Add markers for test selection
    if args.module:
        # Convert module name to directory path
        module_path = os.path.join(TEST_DIR, args.module)
        if os.path.exists(module_path):
            cmd.append(module_path)
        else:
            # Try as a module pattern
            cmd.extend(["-k", args.module])
    
    # Add specific test
    if args.test:
        if os.path.exists(args.test):
            cmd.append(args.test)
        else:
            # Search for the test file
            for root, _, files in os.walk(TEST_DIR):
                for file in files:
                    if args.test in file and file.startswith("test_"):
                        cmd.append(os.path.join(root, file))
                        break
            else:
                # If not found as a file, use as a test case pattern
                cmd.extend(["-k", args.test])
    
    # Add keyword filtering
    if args.keyword:
        cmd.extend(["-k", args.keyword])
    
    # Add coverage if not disabled
    if not args.no_coverage:
        coverage_options = [
            "--cov=" + pkg for pkg in PROJECT_PACKAGES
        ]
        cmd.extend(coverage_options)
        cmd.append("--cov-report=term")
        
        # Add coverage reports
        if args.html_report:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            html_dir = os.path.join(COVERAGE_DIR, f"html_{timestamp}")
            cmd.append(f"--cov-report=html:{html_dir}")
        
        if args.xml_report:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            xml_file = os.path.join(COVERAGE_DIR, f"coverage_{timestamp}.xml")
            cmd.append(f"--cov-report=xml:{xml_file}")
        
        # Add fail-under threshold
        cmd.append(f"--cov-fail-under={args.fail_under}")
    
    # Default to all tests if no specific tests were specified
    if not (args.module or args.test):
        cmd.append(TEST_DIR)
    
    return cmd

def run_tests(cmd):
    """Run the tests with the given command."""
    print(f"Running command: {' '.join(cmd)}")
    
    try:
        result = subprocess.run(cmd, check=False)
        return result.returncode
    except subprocess.CalledProcessError as e:
        print(f"Test execution failed: {e}")
        return e.returncode
    except KeyboardInterrupt:
        print("\nTest execution interrupted by user")
        return 130  # Standard exit code for Ctrl+C

def main():
    """Main function to run tests."""
    args = parse_arguments()
    prepare_environment()
    
    cmd = build_pytest_command(args)
    return_code = run_tests(cmd)
    
    # Print summary
    if return_code == 0:
        print("\n✅ All tests passed successfully!")
    else:
        print(f"\n❌ Tests failed with return code {return_code}")
    
    sys.exit(return_code)

if __name__ == "__main__":
    main() 