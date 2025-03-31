# Monitoring Integration

This guide explains how to integrate Summit SEO with various monitoring systems to track SEO metrics over time and set up alerts for critical issues.

## Overview

Monitoring your website's SEO health over time is crucial for:

1. **Detecting SEO regressions** early before they impact search rankings
2. **Tracking improvements** after implementing recommendations
3. **Setting up alerts** for critical SEO issues
4. **Visualizing SEO trends** through dashboards and reports
5. **Correlating SEO changes** with other business metrics

## Monitoring Integration Example

The Summit SEO package includes monitoring integration examples in `examples/monitoring_integration_example.py` which demonstrates how to:

- Export SEO metrics for Prometheus
- Create Nagios/Icinga2 compatible checks
- Implement a simple alerting system
- Track SEO metrics over time

## Prometheus Integration

[Prometheus](https://prometheus.io/) is a popular open-source monitoring and alerting toolkit. Summit SEO can export metrics in Prometheus format for easy integration.

### Example Implementation

```python
from summit_seo import SummitSEO
from summit_seo.analyzer import SecurityAnalyzer, PerformanceAnalyzer

class PrometheusExporter:
    def __init__(self, url, output_dir="monitoring"):
        self.url = url
        self.output_dir = output_dir
        self.summit = SummitSEO()
        
    def run_check(self):
        analyzers = [SecurityAnalyzer(), PerformanceAnalyzer()]
        results = self.summit.analyze_url(self.url, analyzers=analyzers)
        return results
    
    def generate_prometheus_metrics(self, results):
        metrics = []
        metrics.append("# HELP summit_seo_score SEO score from 0-100")
        metrics.append("# TYPE summit_seo_score gauge")
        
        for analyzer_name, analyzer_result in results.items():
            if hasattr(analyzer_result, "score"):
                score = analyzer_result.score
                metrics.append(f'summit_seo_score{{analyzer="{analyzer_name}"}} {score}')
                
        return "\n".join(metrics)
```

### Prometheus Configuration

Add a scrape config to your `prometheus.yml` file:

```yaml
scrape_configs:
  - job_name: 'summit_seo'
    scrape_interval: 24h
    static_configs:
      - targets: ['your-server:9091']
```

### Grafana Dashboard

Create a Grafana dashboard to visualize your SEO metrics over time. Here's an example JSON dashboard definition:

```json
{
  "title": "SEO Health Dashboard",
  "panels": [
    {
      "title": "SEO Scores",
      "type": "graph",
      "targets": [
        { "expr": "summit_seo_score", "legendFormat": "{{analyzer}}" }
      ]
    },
    {
      "title": "Critical Issues",
      "type": "stat",
      "targets": [
        { "expr": "sum(summit_seo_issues{severity='critical'})" }
      ]
    }
  ]
}
```

## Nagios/Icinga2 Integration

For those using Nagios or Icinga2 for monitoring, Summit SEO can be integrated as a check plugin.

### Example Implementation

```python
def check_seo_health(url, warning_threshold=70, critical_threshold=60):
    """Nagios/Icinga2 plugin for SEO health checks."""
    try:
        summit = SummitSEO()
        results = summit.analyze_url(url, analyzers=[SecurityAnalyzer()])
        
        # Get the security score
        security_score = results["SecurityAnalyzer"].score
        
        # Determine status
        if security_score < critical_threshold:
            print(f"CRITICAL: Security score is {security_score} | score={security_score}")
            return 2
        elif security_score < warning_threshold:
            print(f"WARNING: Security score is {security_score} | score={security_score}")
            return 1
        else:
            print(f"OK: Security score is {security_score} | score={security_score}")
            return 0
    except Exception as e:
        print(f"UNKNOWN: Error checking SEO health - {str(e)}")
        return 3
```

### Nagios Configuration

```
define command {
    command_name    check_seo_health
    command_line    $USER1$/check_seo_health.py -u $ARG1$ -w $ARG2$ -c $ARG3$
}

define service {
    host_name               example-website
    service_description     SEO Health
    check_command           check_seo_health!https://example.com!70!60
    check_interval          1440  # Check once a day
    notification_interval   1440
}
```

## Alerting System

Set up alerts for critical SEO issues using Summit SEO's alerting capabilities.

### Example Implementation

```python
def alert_on_seo_issues(url, threshold=70, alert_handlers=None):
    """Alert when SEO scores fall below thresholds."""
    if alert_handlers is None:
        alert_handlers = []
    
    summit = SummitSEO()
    results = summit.analyze_url(url)
    
    # Check all analyzer scores
    for analyzer_name, analyzer_result in results.items():
        if hasattr(analyzer_result, "score"):
            score = analyzer_result.score
            if score < threshold:
                message = f"SEO Alert: {analyzer_name} score for {url} is {score}, below threshold of {threshold}"
                # Send alerts through all handlers
                for handler in alert_handlers:
                    handler(message)
```

### Alert Handlers

You can implement various alert handlers:

#### Email Alerts

```python
def email_alert(message, recipients=None, sender=None):
    """Send email alerts for SEO issues."""
    import smtplib
    from email.message import EmailMessage
    
    if recipients is None:
        recipients = ["admin@example.com"]
    if sender is None:
        sender = "seo-alerts@example.com"
    
    msg = EmailMessage()
    msg.set_content(message)
    msg["Subject"] = "SEO Alert"
    msg["From"] = sender
    msg["To"] = ", ".join(recipients)
    
    with smtplib.SMTP("smtp.example.com", 587) as server:
        server.starttls()
        server.login("username", "password")
        server.send_message(msg)
```

#### Slack Alerts

```python
def slack_alert(message, webhook_url=None):
    """Send Slack alerts for SEO issues."""
    import requests
    import json
    
    if webhook_url is None:
        webhook_url = "https://hooks.slack.com/services/YOUR/WEBHOOK/URL"
    
    payload = {
        "text": message,
        "username": "SEO Monitor"
    }
    
    requests.post(webhook_url, data=json.dumps(payload))
```

## Scheduled Monitoring

To run SEO checks on a schedule, you can use cron jobs (Linux/Unix) or Task Scheduler (Windows).

### Cron Job Example

```bash
# Run daily SEO checks at 3:00 AM
0 3 * * * cd /path/to/summit-seo && python -m examples.monitoring_integration_example
```

### Docker Container Example

You can also run SEO monitoring in a Docker container:

```Dockerfile
FROM python:3.10-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

# Run monitoring script daily
CMD ["sh", "-c", "while true; do python -m examples.monitoring_integration_example; sleep 86400; done"]
```

## Best Practices

1. **Monitor key pages** - Focus on your most important pages like homepage, product pages, and landing pages
2. **Set appropriate check intervals** - Daily checks are usually sufficient for most websites
3. **Create baselines** - Establish baseline metrics before making changes to your website
4. **Use appropriate thresholds** - Set thresholds based on your specific SEO requirements
5. **Track trends over time** - Look for patterns and trends rather than individual scores
6. **Alert on critical issues only** - Avoid alert fatigue by focusing on important issues
7. **Integrate with existing monitoring** - Leverage your existing monitoring infrastructure
8. **Automate remediation when possible** - Set up automated fixes for common issues 