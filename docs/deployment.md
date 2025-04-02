# Summit SEO Deployment Guide

This guide details the deployment process for the Summit SEO application in a production environment.

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Production Environment Setup](#production-environment-setup)
3. [Deployment Process](#deployment-process)
4. [Monitoring and Logging](#monitoring-and-logging)
5. [Backup and Recovery](#backup-and-recovery)
6. [Scaling](#scaling)
7. [Troubleshooting](#troubleshooting)

## Prerequisites

Before deploying the Summit SEO application, ensure you have:

- A Linux server with at least 4GB RAM and 2 CPU cores
- Docker (20.10+) and Docker Compose (2.0+) installed
- Domain name configured with DNS pointing to your server
- SSL certificates for your domain
- Supabase account and project set up

## Production Environment Setup

### Directory Structure

```
summit-seo/
├── summit_seo/            # Application code
│   ├── web/               # Web components
│   │   ├── api/           # Backend API
│   │   └── temp_next_app/ # Frontend app
├── nginx/                 # Nginx configuration
│   ├── conf/              # Configuration files
│   ├── ssl/               # SSL certificates
│   └── www/               # Static files
├── logs/                  # Application logs
├── monitoring/            # Monitoring stack
│   ├── prometheus/        # Prometheus configuration
│   ├── grafana/           # Grafana dashboards
│   ├── alertmanager/      # Alertmanager configuration
│   ├── loki/              # Loki configuration
│   └── promtail/          # Promtail configuration
├── docker-compose.yml     # Main application services
└── monitoring/docker-compose.yml # Monitoring services
```

### Environment Configuration

1. Create `.env.production` file based on the provided template
2. Configure all necessary environment variables:
   - Database connection details
   - Supabase credentials
   - LiteLLM and API configurations
   - Security settings
   - Monitoring parameters

### SSL Configuration

Place your SSL certificates in the `nginx/ssl/` directory:
- `summit-seo.com.crt` - SSL certificate file
- `summit-seo.com.key` - SSL private key file

## Deployment Process

### Initial Deployment

1. Clone the repository to your production server:
   ```bash
   git clone https://github.com/yourusername/summit-seo.git
   cd summit-seo
   ```

2. Make the deployment script executable and run it:
   ```bash
   chmod +x deploy.sh
   ./deploy.sh
   ```

   This script will:
   - Check for required dependencies
   - Create necessary directories
   - Copy environment variables
   - Build and start Docker containers
   - Verify service status

3. Start the monitoring stack:
   ```bash
   cd monitoring
   docker-compose up -d
   ```

### Automated Deployment with GitHub Actions

The repository includes a GitHub Actions workflow for continuous deployment:

1. Set up the following secrets in your GitHub repository:
   - `SSH_PRIVATE_KEY`: Private SSH key for server access
   - `DEPLOY_HOST`: Server hostname or IP
   - `DEPLOY_USER`: SSH username
   - `DEPLOY_PATH`: Path to deployment directory
   - `DATABASE_URL`: Supabase database connection string
   - `SUPABASE_URL`: Supabase project URL
   - `SUPABASE_KEY`: Supabase anon key
   - `SUPABASE_SERVICE_KEY`: Supabase service key
   - `CORS_ORIGINS`: Allowed origins for CORS
   - `NEXT_PUBLIC_API_URL`: Public API URL
   - `NEXT_PUBLIC_SUPABASE_URL`: Public Supabase URL
   - `NEXT_PUBLIC_SUPABASE_ANON_KEY`: Public Supabase anon key
   - `LITELLM_API_KEY`: LiteLLM API key
   - `LITELLM_DEFAULT_MODEL`: Default LLM model
   - `OPENROUTER_API_KEY`: OpenRouter API key
   - `SESSION_SECRET`: Session secret key
   - `SENTRY_DSN`: Sentry DSN for error tracking
   - `SLACK_WEBHOOK`: Slack webhook for deployment notifications

2. When you push changes to the `main` branch, the workflow will automatically:
   - Copy files to the production server
   - Create the environment file
   - Deploy the application using Docker Compose
   - Verify deployment status
   - Send notifications about the deployment result

## Monitoring and Logging

### Monitoring Stack

The monitoring stack consists of:

1. **Prometheus**: Metrics collection and alerting
2. **Grafana**: Visualization and dashboards
3. **Alertmanager**: Alert routing and notifications
4. **Node Exporter**: Host metrics collection
5. **cAdvisor**: Container metrics collection
6. **Nginx Exporter**: Nginx metrics collection
7. **Loki**: Log aggregation
8. **Promtail**: Log collection agent

Access Monitoring Tools:
- Prometheus: http://your-server-ip:9090
- Grafana: http://your-server-ip:3001 (default credentials: admin/admin)
- Alertmanager: http://your-server-ip:9093

### Log Management

Application logs are stored in the `logs/` directory and are collected by Promtail.

View logs through Grafana's Loki data source or directly with Docker Compose:
```bash
# View real-time logs from all services
docker-compose logs -f

# View logs from a specific service
docker-compose logs -f api
docker-compose logs -f frontend
```

## Backup and Recovery

### Database Backup

Supabase provides automatic backups. Additionally, you can set up manual backups:

```bash
# Create a PostgreSQL dump
docker-compose exec -T db pg_dump -U postgres summit_seo > backups/summit_seo_$(date +%Y%m%d).sql
```

### Application Backup

```bash
# Backup environment and configuration files
tar -czf backups/summit_seo_config_$(date +%Y%m%d).tar.gz .env nginx/conf nginx/ssl
```

### Recovery Process

1. Restore configuration files:
   ```bash
   tar -xzf backups/summit_seo_config_YYYYMMDD.tar.gz
   ```

2. Restore database (if using local PostgreSQL):
   ```bash
   cat backups/summit_seo_YYYYMMDD.sql | docker-compose exec -T db psql -U postgres summit_seo
   ```

3. Redeploy the application:
   ```bash
   ./deploy.sh
   ```

## Scaling

### Horizontal Scaling

To handle increased load, you can scale services horizontally:

```bash
# Scale API service
docker-compose up -d --scale api=3

# Update Nginx configuration for load balancing
```

### Vertical Scaling

For vertical scaling, adjust resource limits in `docker-compose.yml`:

```yaml
services:
  api:
    deploy:
      resources:
        limits:
          cpus: '2'
          memory: 2G
```

## Troubleshooting

### Common Issues

#### Container Startup Failures

Check logs for specific errors:
```bash
docker-compose logs api
```

#### SSL Certificate Issues

Verify certificate files in `nginx/ssl/` directory and check Nginx configuration.

#### Database Connection Problems

Check Supabase connection settings in `.env` file.

### Health Checks

Monitor service health:
```bash
# Check container status
docker-compose ps

# Check API health endpoint
curl https://app.summit-seo.com/api/health

# Check monitoring health
curl http://localhost:9090/-/healthy
```

### Getting Help

If you encounter issues not covered in this guide, please:
1. Check the application logs
2. Review error details in Grafana/Prometheus
3. Consult the project documentation
4. Contact the development team 