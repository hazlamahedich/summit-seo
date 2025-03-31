# Troubleshooting Guide

This guide provides solutions for common issues and errors you might encounter when using Summit SEO. If you're experiencing a problem not listed here, please refer to the [Getting Help](#getting-help) section.

## Table of Contents

1. [Installation Issues](#installation-issues)
2. [Runtime Errors](#runtime-errors)
3. [Analysis Problems](#analysis-problems)
4. [Performance Issues](#performance-issues)
5. [Report Generation Problems](#report-generation-problems)
6. [Advanced Troubleshooting](#advanced-troubleshooting)
7. [Getting Help](#getting-help)

## Installation Issues

### Package Not Found Error

**Error**: `pip install summit-seo` fails with "No matching distribution found for summit-seo"

**Solutions**:
- Verify your internet connection
- Check if PyPI is accessible: `pip install requests`
- Update pip: `pip install --upgrade pip`
- If using a corporate network, check proxy settings or try with `--proxy` flag

### Dependency Installation Failures

**Error**: "Could not build wheels for [dependency]" or "Failed building wheel for [dependency]"

**Solutions**:

For Linux:
```bash
# Ubuntu/Debian
sudo apt-get install build-essential python3-dev libxml2-dev libxslt-dev

# CentOS/RHEL
sudo yum groupinstall "Development Tools"
sudo yum install python3-devel libxml2-devel libxslt-devel
```

For macOS:
```bash
xcode-select --install
brew install libxml2 libxslt
export LDFLAGS="-L/usr/local/opt/libxml2/lib"
export CPPFLAGS="-I/usr/local/opt/libxml2/include"
```

For Windows:
- Install Visual C++ Build Tools
- Try installing a pre-built wheel: `pip install summit-seo --only-binary=:all:`

### Permission Errors During Installation

**Error**: "Permission denied" when installing

**Solutions**:
- Use a virtual environment: `python -m venv venv && source venv/bin/activate`
- Install for current user only: `pip install --user summit-seo`
- On Linux/macOS, use sudo (not recommended): `sudo pip install summit-seo`

### SSL Certificate Verification Failed

**Error**: "SSL: CERTIFICATE_VERIFY_FAILED" during installation

**Solutions**:
```bash
# Update certificates
pip install --upgrade certifi

# If that doesn't work (not recommended for production)
pip install --trusted-host pypi.org --trusted-host files.pythonhosted.org summit-seo
```

## Runtime Errors

### ImportError: Module Not Found

**Error**: `ImportError: No module named 'summit_seo'` or similar import errors

**Solutions**:
- Verify installation: `pip list | grep summit-seo`
- Check the Python environment is the same where you installed the package
- If using virtual environments, ensure it's activated
- Try reinstalling: `pip uninstall summit-seo && pip install summit-seo`

### Command Not Found

**Error**: `summit-seo: command not found` when trying to use the CLI

**Solutions**:
- Verify the installation path is in your PATH variable
- For user installations, make sure `~/.local/bin` is in your PATH
- Try running with the module syntax: `python -m summit_seo`
- Reinstall with: `pip install --force-reinstall summit-seo`

### Version Compatibility Issues

**Error**: "requires Python version X.Y or higher" or dependency version conflicts

**Solutions**:
- Check Python version: `python --version`
- Upgrade Python or install a compatible version
- Install a specific version of Summit SEO: `pip install summit-seo==X.Y.Z`
- Use a separate virtual environment for different projects

## Analysis Problems

### Unable to Connect to Website

**Error**: "Connection refused", "Connection timeout" or "Failed to establish a connection"

**Solutions**:
- Verify the URL is correct and accessible in a browser
- Check network connectivity and DNS resolution
- Check firewall settings that might block outgoing connections
- Try with increased timeout: `--timeout 60`
- For unreachable sites, try with HTML file input instead

### HTTP Error Codes

**Error**: HTTP 403 Forbidden, 429 Too Many Requests, etc.

**Solutions**:
- For 403: The site may be blocking automated access
  - Try setting a custom user agent: `--user-agent "Mozilla/5.0..."`
  - Reduce request rate: `--rate-limit 1`
- For 429: You're being rate limited
  - Reduce request rate: `--rate-limit 0.5`
  - Add more delay between requests: `--request-delay 5`
- For other status codes, refer to HTTP specifications

### JavaScript-Heavy Sites Not Analyzing Correctly

**Error**: Missing content or incomplete analysis due to JavaScript rendering

**Solutions**:
- Use the headless browser option: `--use-browser`
- Set a longer wait time for JavaScript: `--wait-for-js 10`
- For complex sites, consider using the local HTML option after manual loading

### Memory Errors During Analysis

**Error**: "MemoryError", "Killed" or the process terminates unexpectedly

**Solutions**:
- Limit the analysis scope: `--max-pages 100`
- Limit the crawl depth: `--max-depth 2`
- Use memory limiting: `--memory-limit 1024` (MB)
- Run with the incremental option: `--incremental`
- For large sites, split analysis into smaller segments

### Analyzer-Specific Errors

**Error**: Errors from specific analyzers like "SecurityAnalyzer failed" or "Schema validation error"

**Solutions**:
- Disable specific analyzers: `--disable-analyzers security,schema`
- Try updating to the latest version for bug fixes
- Check if the website uses uncommon or invalid structures
- Run with verbose logging for more details: `--log-level debug`

## Performance Issues

### Slow Analysis

**Problem**: Analysis takes too long to complete

**Solutions**:
- Limit the scope: `--max-pages 50 --max-depth 2`
- Disable slow analyzers: `--disable-analyzers performance,accessibility`
- Increase parallelism: `--parallel --max-workers 8`
- Use caching: `--enable-cache`
- For repeat analysis, use the incremental mode: `--incremental`

### High CPU Usage

**Problem**: Analysis consumes excessive CPU resources

**Solutions**:
- Limit parallel processing: `--max-workers 2`
- Use process-based parallelism: `--parallel-mode process`
- Disable intensive analyzers: `--disable-analyzers performance,security`
- Run with lower priority: `nice -n 19 summit-seo analyze...`

### High Memory Consumption

**Problem**: Analysis consumes excessive memory

**Solutions**:
- Set memory limits: `--memory-limit 1024`
- Disable memory-intensive features: `--disable-feature link-graph`
- Process fewer pages at once: `--batch-size 10`
- Use streaming mode when available: `--stream-results`
- Clean up between sites: `--gc-between-sites`

## Report Generation Problems

### Failed to Generate Report

**Error**: "Failed to generate report" or incomplete reports

**Solutions**:
- Check disk space and write permissions
- Try a different output format: `--output-format json`
- Verify the data was collected successfully
- Generate separate reports for each analyzer: `--separate-reports`
- Check for specific format requirements (e.g., template files for custom formats)

### Visualization Errors

**Error**: "Failed to generate visualization" or missing charts

**Solutions**:
- Install optional visualization dependencies: `pip install summit-seo[visualization]`
- Check matplotlib and other visualization libraries are installed
- Try a different chart format: `--chart-format png`
- Use simplified visualizations: `--simple-charts`
- Export raw data and use external tools: `--export-data`

### Invalid Report Format

**Error**: "Invalid report format", corrupted or unreadable reports

**Solutions**:
- Verify format compatibility with your version of Summit SEO
- Try the default format: `--output-format html`
- Check for disk space or file system errors
- Check for special characters in filenames
- Use absolute paths for output files

## Advanced Troubleshooting

### Enabling Debugging and Logging

For detailed troubleshooting, enable debug logging:

```bash
# Enable debug logs
summit-seo analyze --url https://example.com --log-level debug --log-file debug.log

# For more verbose HTTP debugging
summit-seo analyze --url https://example.com --log-level debug --debug-http
```

### Tracing and Profiling

To identify performance bottlenecks:

```bash
# Run with basic profiling
summit-seo analyze --url https://example.com --profile

# Run with detailed profiling (requires Python profilers)
python -m cProfile -o profile.out -m summit_seo analyze --url https://example.com

# Analyze the profile
python -m pstats profile.out
```

### Database and Cache Issues

**Error**: "Failed to connect to cache" or database errors

**Solutions**:
- Check cache configuration: `--cache-config '{"type": "redis", "host": "localhost"}'`
- Clear cache: `summit-seo cache clear`
- Check Redis/database connectivity
- Verify permissions for file-based caches

### Diagnosing Data Collection Issues

For issues with data collection:

```bash
# Capture raw data only without analysis
summit-seo collect --url https://example.com --output raw_data.json

# Check collector functionality
summit-seo diagnose-collector --url https://example.com

# Test network connectivity
summit-seo connectivity-test --url https://example.com
```

### Recovering from Crashes

If Summit SEO crashes during analysis:

```bash
# Resume from last checkpoint
summit-seo analyze --url https://example.com --resume

# Analyze with crash protection
summit-seo analyze --url https://example.com --safe-mode

# Salvage partial data from last run
summit-seo recover --output recovered_data.json
```

## Common Error Messages and Solutions

### "AttributeError: 'NoneType' object has no attribute X"

This often means data expected to be present is missing.

**Solutions**:
- Check if the website is fully accessible
- Verify the page structure matches expectations
- Try with `--lenient-parsing` option
- Check for JavaScript requirements: `--use-browser`

### "TimeoutError: The operation exceeded the time limit"

**Solutions**:
- Increase timeouts: `--timeout 60 --socket-timeout 30`
- Check network connectivity
- Try analyzing during off-peak hours
- Reduce parallel requests: `--max-connections 5`

### "KeyError: 'X'" in Analysis Results

**Solutions**:
- Check analyzer configuration
- Verify the page contains expected elements
- Update to latest version for bug fixes
- Run specific analyzer with detailed logs: `--only-analyzers content --log-level debug`

### "PermissionError: [Errno 13] Permission denied"

**Solutions**:
- Check file and directory permissions
- Use a different output directory with write permissions
- Run with appropriate user permissions
- Specify absolute paths for output files

## Getting Help

If you've tried the solutions above and still encounter issues:

### Generating a Diagnostic Report

```bash
# Generate diagnostic information
summit-seo diagnostics --full --output diagnostic_report.txt

# Run a self-test
summit-seo self-test --all
```

### Reporting Issues

When reporting issues:

1. Include your Summit SEO version: `summit-seo --version`
2. Include Python version: `python --version`
3. Describe your environment (OS, deployment method)
4. Include the full error message and stack trace
5. Share reproduction steps
6. Attach diagnostic reports if possible

### Community Resources

- **Documentation**: [Summit SEO Docs](https://docs.summit-seo.org)
- **GitHub Issues**: [Report bugs](https://github.com/summit-seo/summit-seo/issues)
- **Community Forum**: [Ask questions](https://forum.summit-seo.org)
- **Stack Overflow**: Tag questions with `summit-seo`
- **Discord Channel**: [Join for real-time help](https://discord.gg/summit-seo)

### Commercial Support

For enterprise users or critical applications:

- **Email Support**: support@summit-seo.org
- **Priority Support Plans**: [Enterprise Support Options](https://summit-seo.org/enterprise)
- **Training and Consulting**: [Professional Services](https://summit-seo.org/services)

Remember to keep your Summit SEO installation updated to benefit from bug fixes and improvements:

```bash
pip install --upgrade summit-seo
```

This troubleshooting guide covers the most common issues you might encounter when using Summit SEO. For more specific problems, please reach out to the community or support channels. 