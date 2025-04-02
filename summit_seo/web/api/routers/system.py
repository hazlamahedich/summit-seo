"""
System information router for Summit SEO API.
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from typing import Any, Dict, List, Optional
import platform
import psutil
import os
import time
import datetime
import socket
import uuid
import json

from ..core.deps import get_current_superuser, get_settings_service
from ..core.config import settings as app_settings
from ..services import SettingScope
from ..models.common import StandardResponse

router = APIRouter()

@router.get("/info", response_model=StandardResponse)
async def get_system_info(
    current_user: Dict[str, Any] = Depends(get_current_superuser)
) -> Any:
    """
    Get system information.
    
    Only accessible by superusers.
    """
    try:
        # Get host information
        hostname = socket.gethostname()
        ip_address = socket.gethostbyname(hostname)
        
        # Get system information
        system_info = {
            "system": {
                "platform": platform.system(),
                "platform_version": platform.version(),
                "platform_release": platform.release(),
                "architecture": platform.machine(),
                "processor": platform.processor(),
                "python_version": platform.python_version(),
                "hostname": hostname,
                "ip_address": ip_address
            },
            "memory": {
                "total": psutil.virtual_memory().total,
                "available": psutil.virtual_memory().available,
                "percent_used": psutil.virtual_memory().percent,
            },
            "disk": {
                "total": psutil.disk_usage('/').total,
                "used": psutil.disk_usage('/').used,
                "free": psutil.disk_usage('/').free,
                "percent_used": psutil.disk_usage('/').percent,
            },
            "cpu": {
                "cores_physical": psutil.cpu_count(logical=False),
                "cores_logical": psutil.cpu_count(logical=True),
                "percent_used": psutil.cpu_percent(interval=1),
            },
            "app": {
                "version": app_settings.VERSION,
                "api_version": app_settings.API_VERSION,
                "environment": app_settings.ENVIRONMENT,
                "debug": app_settings.DEBUG,
            },
            "timestamp": datetime.datetime.utcnow().isoformat(),
        }
        
        return {
            "status": "success",
            "data": system_info
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "code": "SYSTEM_INFO_ERROR",
                "message": f"Error retrieving system information: {str(e)}",
                "details": {}
            }
        )

@router.get("/status", response_model=StandardResponse)
async def get_service_status() -> Any:
    """
    Get API service status.
    
    This endpoint is publicly accessible.
    """
    # Get basic service status - useful for monitoring
    current_time = datetime.datetime.utcnow()
    
    try:
        # Get server load average
        load_avg = os.getloadavg() if hasattr(os, 'getloadavg') else [0, 0, 0]
        
        # Get memory usage
        memory = psutil.virtual_memory()
        
        status_data = {
            "status": "operational",
            "environment": app_settings.ENVIRONMENT,
            "version": app_settings.VERSION,
            "api_version": app_settings.API_VERSION,
            "timestamp": current_time.isoformat(),
            "uptime": time.time() - psutil.boot_time(),
            "load": {
                "1m": load_avg[0],
                "5m": load_avg[1],
                "15m": load_avg[2]
            },
            "memory": {
                "used_percent": memory.percent
            },
            "instance_id": str(uuid.uuid4())  # This would be stored/loaded in a real implementation
        }
        
        return {
            "status": "success",
            "data": status_data
        }
    except Exception as e:
        return {
            "status": "error",
            "data": {
                "status": "degraded",
                "error": str(e),
                "timestamp": current_time.isoformat()
            }
        }

@router.post("/restart", status_code=status.HTTP_202_ACCEPTED, response_model=StandardResponse)
async def restart_service(
    current_user: Dict[str, Any] = Depends(get_current_superuser)
) -> Any:
    """
    Request a service restart.
    
    Only accessible by superusers.
    In a real implementation, this would trigger a restart process.
    """
    # This is a placeholder - in a real implementation, this would
    # trigger a restart process or send a signal to a process manager
    restart_time = datetime.datetime.utcnow() + datetime.timedelta(seconds=30)
    
    return {
        "status": "success",
        "data": {
            "status": "restart_requested",
            "message": "Service restart has been requested",
            "estimated_completion": restart_time.isoformat(),
            "request_id": str(uuid.uuid4())
        }
    }

@router.get("/config", response_model=StandardResponse)
async def get_system_config(
    prefix: Optional[str] = Query(None, description="Filter settings by prefix"),
    current_user: Dict[str, Any] = Depends(get_current_superuser)
) -> Any:
    """
    Get system configuration settings.
    
    Only accessible by superusers.
    
    Args:
        prefix: Optional prefix to filter settings
    """
    settings_service = get_settings_service(use_rls_bypass=True)
    
    try:
        if prefix:
            # Get settings with prefix
            config_data = await settings_service.get_settings_by_prefix(
                prefix=prefix,
                scope=SettingScope.SYSTEM
            )
        else:
            # Get all system settings
            result = await settings_service.get_all_settings(
                scope=SettingScope.SYSTEM,
                page=1,
                page_size=1000  # Large value to get all settings
            )
            
            # Convert to dictionary for easier access
            config_data = {}
            for setting in result["data"]:
                try:
                    # Parse the JSON value
                    config_data[setting["key"]] = json.loads(setting["value"])
                except:
                    # If parsing fails, use the raw value
                    config_data[setting["key"]] = setting["value"]
        
        return {
            "status": "success",
            "data": config_data
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "code": "CONFIG_ERROR",
                "message": f"Error retrieving system configuration: {str(e)}",
                "details": {}
            }
        )

@router.get("/health", response_model=StandardResponse)
async def health_check() -> Any:
    """
    Health check endpoint for monitoring.
    
    This endpoint is publicly accessible and used by health checks.
    """
    # Check if the service is healthy
    # In a real implementation, this would check database
    # connectivity, external services, etc.
    
    return {
        "status": "success",
        "data": {
            "status": "healthy",
            "timestamp": datetime.datetime.utcnow().isoformat(),
            "version": app_settings.VERSION,
            "api_version": app_settings.API_VERSION
        }
    } 