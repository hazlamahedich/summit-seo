#!/usr/bin/env python3
"""
CI/CD Integration Example for Summit SEO

This example demonstrates how to integrate Summit SEO into various CI/CD pipelines
to automate SEO analysis as part of your deployment workflow.

It provides examples for:
1. GitHub Actions integration
2. Jenkins pipeline integration
3. GitLab CI integration
4. CircleCI integration
5. Using Summit SEO as a quality gate

The example includes configuration snippets and Python code to run the analysis
and interpret results in an automated environment.
"""

import os
import sys
import json
from argparse import ArgumentParser
from typing import Dict, List, Optional, Union, Any

# Import Summit SEO components
from summit_seo import SummitSEO
from summit_seo.analyzer import (
    SecurityAnalyzer,
    PerformanceAnalyzer,
    AccessibilityAnalyzer,
    MobileFriendlyAnalyzer,
)
from summit_seo.reporter import JSONReporter, HTMLReporter
from summit_seo.parallel import ParallelManager

# Exit codes
EXIT_SUCCESS = 0
EXIT_FAILURE = 1
EXIT_WARNING = 2


class CICDAnalyzer:
    """
    Utility class for running Summit SEO analysis in CI/CD environments.
    
    This class provides methods to run analysis, check against thresholds,
    and generate appropriate exit codes and reports for CI/CD pipelines.
    """
    
    def __init__(
        self,
        url: str,
        output_dir: str = "reports",
        threshold_scores: Optional[Dict[str, float]] = None,
        analyzers: Optional[List[str]] = None,
        parallel: bool = True,
        verbose: bool = False,
    ):
        """
        Initialize the CI/CD analyzer.
        
        Args:
            url: The URL to analyze
            output_dir: Directory to store output reports
            threshold_scores: Minimum scores required for each analyzer to pass
            analyzers: List of analyzers to run (runs all if None)
            parallel: Whether to run analyzers in parallel
            verbose: Whether to output detailed progress information
        """
        self.url = url
        self.output_dir = output_dir
        self.threshold_scores = threshold_scores or {
            "security": 70.0,
            "performance": 65.0,
            "accessibility": 60.0,
            "mobile_friendly": 70.0,
            "overall": 65.0,
        }
        self.analyzers = analyzers or [
            "security",
            "performance",
            "accessibility",
            "mobile_friendly",
        ]
        self.parallel = parallel
        self.verbose = verbose
        self.results = {}
        
        # Create output directory if it doesn't exist
        os.makedirs(output_dir, exist_ok=True)
        
        # Initialize Summit SEO
        self.summit = SummitSEO()
        
    def run_analysis(self) -> Dict[str, Any]:
        """
        Run the analysis with the configured analyzers.
        
        Returns:
            Dictionary containing analysis results
        """
        if self.verbose:
            print(f"Starting analysis of {self.url}")
            
        # Configure analyzers
        analyzer_instances = []
        if "security" in self.analyzers:
            analyzer_instances.append(SecurityAnalyzer())
        if "performance" in self.analyzers:
            analyzer_instances.append(PerformanceAnalyzer())
        if "accessibility" in self.analyzers:
            analyzer_instances.append(AccessibilityAnalyzer())
        if "mobile_friendly" in self.analyzers:
            analyzer_instances.append(MobileFriendlyAnalyzer())
        
        # Run analysis
        if self.parallel:
            manager = ParallelManager(max_workers=len(analyzer_instances))
            self.results = self.summit.analyze_url(
                self.url, 
                analyzers=analyzer_instances,
                parallel_manager=manager
            )
        else:
            self.results = self.summit.analyze_url(
                self.url, 
                analyzers=analyzer_instances
            )
            
        # Generate reports
        self._generate_reports()
        
        if self.verbose:
            print(f"Analysis completed. Reports saved to {self.output_dir}")
            
        return self.results
    
    def _generate_reports(self) -> None:
        """Generate JSON and HTML reports from the analysis results."""
        # JSON Report
        json_reporter = JSONReporter(
            output_file=os.path.join(self.output_dir, "report.json")
        )
        json_reporter.generate_report(self.results)
        
        # HTML Report
        html_reporter = HTMLReporter(
            output_file=os.path.join(self.output_dir, "report.html")
        )
        html_reporter.generate_report(self.results)
    
    def check_thresholds(self) -> Dict[str, bool]:
        """
        Check if analysis scores meet the defined thresholds.
        
        Returns:
            Dictionary mapping analyzer names to pass/fail status
        """
        if not self.results:
            raise ValueError("Analysis has not been run yet")
        
        status = {}
        overall_score = 0.0
        count = 0
        
        for analyzer_name, analyzer_result in self.results.items():
            if hasattr(analyzer_result, "score"):
                score = analyzer_result.score
                threshold = self.threshold_scores.get(analyzer_name.lower(), 0.0)
                status[analyzer_name] = score >= threshold
                
                if self.verbose:
                    result = "PASS" if score >= threshold else "FAIL"
                    print(f"{analyzer_name}: {score:.1f}/100 - {result} (threshold: {threshold})")
                
                overall_score += score
                count += 1
        
        # Calculate overall score
        if count > 0:
            overall_score /= count
            overall_threshold = self.threshold_scores.get("overall", 0.0)
            status["Overall"] = overall_score >= overall_threshold
            
            if self.verbose:
                result = "PASS" if overall_score >= overall_threshold else "FAIL"
                print(f"Overall: {overall_score:.1f}/100 - {result} (threshold: {overall_threshold})")
        
        return status
    
    def get_exit_code(self) -> int:
        """
        Determine the appropriate exit code based on analysis results.
        
        Returns:
            EXIT_SUCCESS if all checks pass
            EXIT_WARNING if only non-critical checks fail
            EXIT_FAILURE if any critical check fails
        """
        status = self.check_thresholds()
        
        # Critical analyzers (failing these should fail the build)
        critical = ["security", "Security"]
        
        # Check if any critical analyzer failed
        for analyzer in critical:
            if analyzer in status and not status[analyzer]:
                return EXIT_FAILURE
        
        # Check if overall score failed
        if "Overall" in status and not status["Overall"]:
            return EXIT_WARNING
            
        # Check if more than half of the analyzers failed
        failed = sum(1 for status_val in status.values() if not status_val)
        if failed > len(status) / 2:
            return EXIT_WARNING
            
        return EXIT_SUCCESS


def main():
    """Command-line entry point for running the CI/CD integration example."""
    parser = ArgumentParser(description="Summit SEO CI/CD Integration Example")
    parser.add_argument("url", help="URL to analyze")
    parser.add_argument("--output-dir", default="reports", help="Output directory for reports")
    parser.add_argument("--no-parallel", action="store_true", help="Disable parallel processing")
    parser.add_argument("--verbose", action="store_true", help="Enable verbose output")
    args = parser.parse_args()
    
    analyzer = CICDAnalyzer(
        url=args.url,
        output_dir=args.output_dir,
        parallel=not args.no_parallel,
        verbose=args.verbose,
    )
    
    # Run analysis
    analyzer.run_analysis()
    
    # Determine exit code based on results
    exit_code = analyzer.get_exit_code()
    
    # In CI/CD environments, this exit code can be used to determine if the pipeline should fail
    sys.exit(exit_code)


if __name__ == "__main__":
    main()


# CI/CD Configuration Examples

"""
# GitHub Actions Workflow Example
# .github/workflows/seo-analysis.yml
"""
GITHUB_WORKFLOW = """
name: SEO Analysis

on:
  push:
    branches: [ main ]
  pull_request:
    branches: [ main ]
  schedule:
    - cron: '0 0 * * 1'  # Run weekly on Mondays

jobs:
  analyze:
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.10'
        
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install summit-seo
        
    - name: Run SEO analysis
      run: |
        python -m summit_seo.cli analyze https://example.com --output-dir reports
        
    - name: Check thresholds with custom script
      run: |
        python examples/cicd_integration_example.py https://example.com --output-dir reports --verbose
      continue-on-error: true  # Optional: decide if you want to fail the build or just warn
        
    - name: Upload reports
      uses: actions/upload-artifact@v3
      with:
        name: seo-reports
        path: reports/
"""

"""
# Jenkins Pipeline Example
# Jenkinsfile
"""
JENKINS_PIPELINE = """
pipeline {
    agent {
        docker {
            image 'python:3.10'
        }
    }
    
    stages {
        stage('Setup') {
            steps {
                sh 'pip install summit-seo'
            }
        }
        
        stage('Analyze') {
            steps {
                sh 'python -m summit_seo.cli analyze https://example.com --output-dir reports'
            }
        }
        
        stage('Check Thresholds') {
            steps {
                script {
                    def exitCode = sh(
                        script: 'python examples/cicd_integration_example.py https://example.com --output-dir reports --verbose',
                        returnStatus: true
                    )
                    
                    if (exitCode == 1) {
                        currentBuild.result = 'FAILURE'
                        error('SEO analysis failed critical checks')
                    } else if (exitCode == 2) {
                        currentBuild.result = 'UNSTABLE'
                        echo 'SEO analysis warnings detected'
                    }
                }
            }
        }
    }
    
    post {
        always {
            archiveArtifacts artifacts: 'reports/**', fingerprint: true
        }
    }
}
"""

"""
# GitLab CI Example
# .gitlab-ci.yml
"""
GITLAB_CI = """
stages:
  - test
  - deploy

seo-analysis:
  stage: test
  image: python:3.10
  script:
    - pip install summit-seo
    - python -m summit_seo.cli analyze https://example.com --output-dir reports
    - python examples/cicd_integration_example.py https://example.com --output-dir reports --verbose
  artifacts:
    paths:
      - reports/
    expire_in: 1 week
  allow_failure: true  # Optional: decide if you want to fail the pipeline or just warn
"""

"""
# CircleCI Example
# .circleci/config.yml
"""
CIRCLECI_CONFIG = """
version: 2.1

jobs:
  seo-analysis:
    docker:
      - image: cimg/python:3.10
    steps:
      - checkout
      - run:
          name: Install dependencies
          command: pip install summit-seo
      - run:
          name: Run SEO analysis
          command: python -m summit_seo.cli analyze https://example.com --output-dir reports
      - run:
          name: Check thresholds
          command: python examples/cicd_integration_example.py https://example.com --output-dir reports --verbose
          when: always  # Run even if previous steps failed
      - store_artifacts:
          path: reports
          destination: seo-reports
"""

"""
# Pre-deployment Quality Gate Example
# This script can be used in any CI/CD system as a quality gate before deployment
"""
PRE_DEPLOYMENT_SCRIPT = """
#!/bin/bash
set -e

# Install dependencies
pip install summit-seo

# Run analysis
python -m summit_seo.cli analyze https://staging.example.com --output-dir reports

# Check if results meet thresholds
python examples/cicd_integration_example.py https://staging.example.com --output-dir reports --verbose

# Store exit code
EXIT_CODE=$?

if [ $EXIT_CODE -eq 0 ]; then
    echo "SEO analysis passed! Proceeding with deployment."
    # Add deployment commands here
elif [ $EXIT_CODE -eq 2 ]; then
    echo "SEO analysis has warnings. Deployment will proceed, but please review reports."
    # Add deployment commands here, possibly with a warning flag
else
    echo "SEO analysis failed! Deployment aborted."
    exit 1
fi
""" 