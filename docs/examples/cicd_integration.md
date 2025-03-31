# CI/CD Integration

This guide explains how to integrate Summit SEO into your Continuous Integration/Continuous Deployment (CI/CD) pipelines to automate SEO analysis as part of your development workflow.

## Overview

Integrating SEO analysis into your CI/CD pipeline allows you to:

1. **Detect SEO issues early** in the development process
2. **Enforce SEO standards** before code is deployed to production
3. **Track SEO performance** over time with historical data
4. **Automate regular SEO audits** without manual intervention
5. **Use SEO metrics as quality gates** for deployments

## Example Implementation

The Summit SEO package includes a CI/CD integration example in `examples/cicd_integration_example.py` which demonstrates how to:

- Run SEO analysis in an automated environment
- Check results against configurable thresholds
- Generate appropriate exit codes for CI/CD systems
- Create and store reports for later review

## Usage

The CI/CD integration example can be used directly from the command line:

```bash
python examples/cicd_integration_example.py https://example.com --output-dir reports --verbose
```

The script will:
1. Run an SEO analysis on the specified URL
2. Generate HTML and JSON reports in the output directory
3. Check results against default thresholds
4. Return an exit code based on the results:
   - `0`: All checks passed
   - `1`: Critical checks failed (e.g., security issues)
   - `2`: Warning level (some non-critical checks failed)

## Integration Examples

### GitHub Actions

Create a file at `.github/workflows/seo-analysis.yml`:

```yaml
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
```

### Jenkins Pipeline

Create a `Jenkinsfile` in your repository:

```groovy
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
```

### GitLab CI

Create a `.gitlab-ci.yml` file:

```yaml
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
```

### CircleCI

Create a `.circleci/config.yml` file:

```yaml
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
```

## Quality Gate Example

You can use Summit SEO as a quality gate before deployment with a script like this:

```bash
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
```

## Customizing Thresholds

You can customize the threshold scores for each analyzer by modifying the `threshold_scores` parameter in the `CICDAnalyzer` class. The default thresholds are:

- Security: 70.0
- Performance: 65.0
- Accessibility: 60.0
- Mobile Friendly: 70.0
- Overall: 65.0

Example of custom thresholds:

```python
analyzer = CICDAnalyzer(
    url="https://example.com",
    threshold_scores={
        "security": 80.0,  # Higher security requirement
        "performance": 70.0,
        "accessibility": 65.0,
        "mobile_friendly": 75.0,
        "overall": 70.0,
    }
)
```

## Best Practices

1. **Run on staging environments** before production deployments
2. **Set reasonable thresholds** that align with your SEO goals
3. **Store historical reports** to track improvements over time
4. **Schedule regular analyses** (weekly or after major changes)
5. **Use notifications** to alert team members of SEO issues
6. **Consider treating security issues as critical** to block deployments
7. **Keep non-critical issues as warnings** to avoid blocking deployments unnecessarily 