# System Requirements and Installation Guide

This guide provides detailed information about the system requirements for running Summit SEO and step-by-step installation instructions for various environments.

## Table of Contents

1. [System Requirements](#system-requirements)
2. [Installation](#installation)
3. [Verifying Installation](#verifying-installation)
4. [Advanced Installation Options](#advanced-installation-options)
5. [Docker Installation](#docker-installation)
6. [Cloud Deployment](#cloud-deployment)
7. [Troubleshooting](#troubleshooting)

## System Requirements

### Hardware Requirements

Summit SEO is designed to be efficient, but analyzing large websites can be resource-intensive. Here are the recommended hardware specifications:

| Usage | CPU | RAM | Disk Space |
|-------|-----|-----|------------|
| Small websites (<100 pages) | 2+ cores | 4GB+ | 1GB+ |
| Medium websites (100-1000 pages) | 4+ cores | 8GB+ | 5GB+ |
| Large websites (>1000 pages) | 8+ cores | 16GB+ | 20GB+ |
| Enterprise usage | 16+ cores | 32GB+ | 100GB+ SSD |

### Software Requirements

#### Operating Systems

Summit SEO is compatible with the following operating systems:

- **Linux**: Ubuntu 18.04+, Debian 10+, CentOS 7+, Red Hat Enterprise Linux 7+
- **macOS**: 10.14 (Mojave)+ 
- **Windows**: Windows 10, Windows Server 2016+

#### Python Requirements

- Python 3.8 or higher
- pip (Python package installer)
- venv or virtualenv (recommended for virtual environments)

#### Additional System Dependencies

These dependencies may need to be installed separately depending on your OS:

- **Required**:
  - OpenSSL (for secure connections)
  - libxml2 and libxslt (for HTML parsing)
  - zlib (for compression)

- **Optional** (for enhanced functionality):
  - libmagic (for file type detection)
  - Pillow dependencies (for image processing)
  - ffmpeg (for media analysis)

### Network Requirements

- Outbound HTTP/HTTPS connectivity to analyze external websites
- Bandwidth appropriate for site analysis (at least 10 Mbps recommended)
- No NAT or firewall restrictions on outbound connections

## Installation

### Standard Installation

The simplest way to install Summit SEO is using pip:

```bash
pip install summit-seo
```

### Installation with Optional Dependencies

To install Summit SEO with all optional dependencies:

```bash
pip install summit-seo[all]
```

Or select specific extra packages:

```bash
# For performance analysis features
pip install summit-seo[performance]

# For accessibility analysis features
pip install summit-seo[accessibility]

# For schema analysis features
pip install summit-seo[schema]

# For security analysis features
pip install summit-seo[security]
```

### Installation from Source

For the latest development version or custom configurations:

```bash
# Clone the repository
git clone https://github.com/summit-seo/summit-seo.git
cd summit-seo

# Create and activate a virtual environment (recommended)
python -m venv venv
source venv/bin/activate  # On Windows, use: venv\Scripts\activate

# Install dependencies and the package in development mode
pip install -e .
```

### OS-Specific Installation

#### Ubuntu/Debian

Install system dependencies:

```bash
sudo apt-get update
sudo apt-get install -y python3 python3-pip python3-venv libxml2-dev libxslt-dev python3-dev zlib1g-dev libssl-dev
```

Then install Summit SEO:

```bash
python3 -m venv venv
source venv/bin/activate
pip install summit-seo
```

#### macOS

Using Homebrew:

```bash
# Install Homebrew if not already installed
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Install dependencies
brew install python3 libxml2 libxslt openssl

# Create virtual environment and install Summit SEO
python3 -m venv venv
source venv/bin/activate
pip install summit-seo
```

#### Windows

1. Install Python from [python.org](https://www.python.org/downloads/windows/)
2. During installation, check "Add Python to PATH"
3. Open Command Prompt as Administrator:

```cmd
# Create virtual environment
python -m venv venv
venv\Scripts\activate

# Install Summit SEO
pip install summit-seo
```

## Verifying Installation

After installation, verify that Summit SEO works correctly:

```bash
# Check the version
summit-seo --version

# Run a simple analysis test
summit-seo analyze --url https://example.com --output-format json --output-file test.json
```

If these commands execute without errors, Summit SEO is installed correctly.

## Advanced Installation Options

### Installing in Isolated Environments

#### Using virtualenv

```bash
pip install virtualenv
virtualenv summit-env
source summit-env/bin/activate  # On Windows: summit-env\Scripts\activate
pip install summit-seo
```

#### Using conda

```bash
conda create -n summit-env python=3.9
conda activate summit-env
pip install summit-seo
```

### Installing Multiple Versions

If you need multiple versions for different projects:

```bash
# In different virtual environments
python -m venv venv-1.0
source venv-1.0/bin/activate
pip install summit-seo==1.0.0

python -m venv venv-2.0
source venv-2.0/bin/activate
pip install summit-seo==2.0.0
```

### Offline Installation

For environments without internet access:

```bash
# On a machine with internet access
pip download summit-seo -d ./summit-seo-packages
pip download summit-seo[all] -d ./summit-seo-packages  # Include dependencies

# Transfer the directory to the offline machine
# On the offline machine
pip install --no-index --find-links=./summit-seo-packages summit-seo
```

## Docker Installation

Summit SEO is available as a Docker image for containerized deployment.

### Using the Official Docker Image

```bash
# Pull the latest image
docker pull summitseo/summit-seo:latest

# Run a simple analysis
docker run --rm summitseo/summit-seo:latest analyze --url https://example.com
```

### Building a Custom Docker Image

Create a `Dockerfile`:

```dockerfile
FROM python:3.9-slim

RUN apt-get update && apt-get install -y \
    libxml2-dev \
    libxslt-dev \
    zlib1g-dev \
    libssl-dev \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install summit-seo[all]

ENTRYPOINT ["summit-seo"]
CMD ["--help"]
```

Build and run:

```bash
docker build -t my-summit-seo .
docker run --rm my-summit-seo analyze --url https://example.com
```

### Docker Compose Setup

Create a `docker-compose.yml` file:

```yaml
version: '3'
services:
  summit-seo:
    image: summitseo/summit-seo:latest
    volumes:
      - ./config:/app/config
      - ./reports:/app/reports
    command: analyze --config /app/config/config.json --output-file /app/reports/report.html
```

Run with:

```bash
docker-compose up
```

## Cloud Deployment

### AWS Deployment

#### EC2 Installation

1. Launch an EC2 instance (recommended: t3.medium or larger)
2. SSH into the instance
3. Install Summit SEO:

```bash
sudo yum update -y  # For Amazon Linux
sudo yum install -y python3 python3-pip python3-devel gcc libxml2-devel libxslt-devel
pip3 install --user summit-seo
```

#### AWS Lambda Deployment

Create a Lambda function with Summit SEO:

1. Create a deployment package:

```bash
mkdir lambda-package
cd lambda-package
pip install summit-seo -t .
```

2. Create a Lambda handler function `lambda_function.py`:

```python
from summit_seo import SummitSEO

def lambda_handler(event, context):
    url = event.get('url', 'https://example.com')
    seo = SummitSEO()
    result = seo.analyze(url)
    return result.to_dict()
```

3. Zip the package and upload to Lambda
4. Configure with at least 1GB memory and 5-minute timeout

### Google Cloud Deployment

#### Compute Engine

Similar to EC2 installation above, but using:

```bash
sudo apt-get update
sudo apt-get install -y python3 python3-pip python3-venv libxml2-dev libxslt-dev
pip3 install --user summit-seo
```

#### Cloud Functions

Create a Cloud Function with Summit SEO:

```python
from summit_seo import SummitSEO

def analyze_seo(request):
    request_json = request.get_json(silent=True)
    url = request_json.get('url', 'https://example.com')
    
    seo = SummitSEO()
    result = seo.analyze(url)
    
    return result.to_dict()
```

Deploy with:

```bash
gcloud functions deploy analyze_seo --runtime python39 --trigger-http --memory=2048MB --timeout=540s
```

## Troubleshooting

### Common Installation Issues

#### Missing System Dependencies

**Symptom**: Error about missing libraries during pip install

**Solution**:
```bash
# Ubuntu/Debian
sudo apt-get install libxml2-dev libxslt-dev zlib1g-dev

# RHEL/CentOS
sudo yum install libxml2-devel libxslt-devel zlib-devel

# macOS
brew install libxml2 libxslt
```

#### SSL Certificate Verification Errors

**Symptom**: SSL errors when analyzing HTTPS websites

**Solution**:
```bash
pip install --upgrade certifi
```

For persistent issues, you may need to update your OpenSSL installation.

#### Memory Errors During Analysis

**Symptom**: Process killed or out of memory errors

**Solution**:
- Use the `--memory-limit` flag to set a maximum memory usage
- Analyze fewer pages at once
- Increase system swap space

### Version Compatibility

| Summit SEO Version | Python Compatibility | Key Dependencies | 
|--------------------|-----------------------|-----------------|
| 1.0.x | Python 3.8, 3.9 | Beautiful Soup 4.9+, Requests 2.25+ |
| 2.0.x | Python 3.8, 3.9, 3.10 | Beautiful Soup 4.10+, Requests 2.27+ |
| 3.0.x | Python 3.9, 3.10, 3.11 | Beautiful Soup 4.11+, Requests 2.28+ |

### Getting Help

If you encounter issues not covered in this guide:

1. Check the [Troubleshooting Guide](troubleshooting.md) for specific errors
2. Visit the [GitHub Issues](https://github.com/summit-seo/summit-seo/issues) page
3. Join the [Community Forum](https://forum.summit-seo.org)
4. Contact support at support@summit-seo.org

## Uninstallation

To completely remove Summit SEO:

```bash
pip uninstall summit-seo

# To also remove all dependencies (use with caution)
pip freeze | grep -i summit | xargs pip uninstall -y
```

This guide covers the essential information for installing and configuring Summit SEO in various environments. For more detailed configuration options, refer to the [Configuration Guide](configuration.md). 