#!/bin/bash

# Summit SEO Deployment Script
# This script automates the deployment of the Summit SEO application

set -e

echo "📦 Summit SEO Deployment Script"
echo "==============================="

# Check if Docker and Docker Compose are installed
if ! [ -x "$(command -v docker)" ]; then
  echo "🚫 Error: Docker is not installed." >&2
  exit 1
fi

if ! [ -x "$(command -v docker-compose)" ]; then
  echo "🚫 Error: Docker Compose is not installed." >&2
  exit 1
fi

# Check if .env.production exists
if [ ! -f ".env.production" ]; then
  echo "🚫 Error: .env.production file not found. Please create it from the template." >&2
  exit 1
fi

# Create necessary directories
echo "📁 Creating necessary directories..."
mkdir -p logs
mkdir -p nginx/conf
mkdir -p nginx/ssl
mkdir -p nginx/www

# Copy environment variables
echo "🔐 Setting up environment variables..."
cp .env.production .env

# Check for SSL certificates
if [ ! -f "nginx/ssl/summit-seo.com.crt" ] || [ ! -f "nginx/ssl/summit-seo.com.key" ]; then
  echo "⚠️  Warning: SSL certificates not found in nginx/ssl/ directory."
  echo "   You will need to add them before enabling HTTPS."
  read -p "Continue without SSL (production will use HTTP only)? (y/n) " -n 1 -r
  echo
  if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "🚫 Deployment aborted." >&2
    exit 1
  fi
  
  # Update nginx config to use HTTP only
  sed -i 's/listen 443 ssl;/# listen 443 ssl;/g' nginx/conf/default.conf
  sed -i 's/return 301 https:\/\/$host$request_uri;/# return 301 https:\/\/$host$request_uri;/g' nginx/conf/default.conf
fi

# Build and start the containers
echo "🔨 Building Docker containers..."
docker-compose build

echo "🚀 Starting services..."
docker-compose up -d

# Check if containers are running
echo "🔍 Checking service status..."
sleep 10  # Give services time to start

if [ "$(docker-compose ps -q api | wc -l)" -eq 0 ]; then
  echo "🚫 Error: API container failed to start. Check logs with 'docker-compose logs api'." >&2
  exit 1
fi

if [ "$(docker-compose ps -q frontend | wc -l)" -eq 0 ]; then
  echo "🚫 Error: Frontend container failed to start. Check logs with 'docker-compose logs frontend'." >&2
  exit 1
fi

if [ "$(docker-compose ps -q nginx | wc -l)" -eq 0 ]; then
  echo "🚫 Error: Nginx container failed to start. Check logs with 'docker-compose logs nginx'." >&2
  exit 1
fi

echo "✅ All services are running!"
echo "🌐 Access your application at: http://localhost or http://app.summit-seo.com (if DNS is configured)"
echo
echo "📊 Useful commands:"
echo "  - View all logs: docker-compose logs -f"
echo "  - View API logs: docker-compose logs -f api"
echo "  - View frontend logs: docker-compose logs -f frontend"
echo "  - Stop services: docker-compose down"
echo "  - Restart services: docker-compose restart"
echo
echo "✨ Deployment complete!" 