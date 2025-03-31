from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.utils import get_openapi
from fastapi.responses import JSONResponse
import logging
import time
from typing import Dict, Any, Optional

# Import routers (will be created later)
from .routers import auth, users, projects, analyses, settings, system

# Create FastAPI app
app = FastAPI(
    title="Summit SEO API",
    description="REST API for Summit SEO web application",
    version="1.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_url="/api/openapi.json"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Set to specific origins in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger("summit_seo_api")

# Request logging middleware
@app.middleware("http")
async def log_requests(request, call_next):
    start_time = time.time()
    
    # Process the request
    response = await call_next(request)
    
    # Log request details
    process_time = time.time() - start_time
    logger.info(
        f"Request: {request.method} {request.url.path} "
        f"Status: {response.status_code} "
        f"Time: {process_time:.4f}s"
    )
    
    return response

# Custom exception handler for standardized error responses
@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    error_response = {
        "status": "error",
        "error": {
            "code": exc.detail.get("code", "UNKNOWN_ERROR") if isinstance(exc.detail, dict) else "UNKNOWN_ERROR",
            "message": exc.detail.get("message", str(exc.detail)) if isinstance(exc.detail, dict) else str(exc.detail),
            "details": exc.detail.get("details", {}) if isinstance(exc.detail, dict) else {}
        }
    }
    return JSONResponse(
        status_code=exc.status_code,
        content=error_response
    )

# Include routers
app.include_router(auth.router, prefix="/api/v1/auth", tags=["Authentication"])
app.include_router(users.router, prefix="/api/v1/users", tags=["Users"])
app.include_router(projects.router, prefix="/api/v1/projects", tags=["Projects"])
app.include_router(analyses.router, prefix="/api/v1/projects/{project_id}/analyses", tags=["Analyses"])
app.include_router(settings.router, prefix="/api/v1/settings", tags=["Settings"])
app.include_router(system.router, prefix="/api/v1/system", tags=["System"])

# Root endpoint
@app.get("/api/v1", tags=["Root"])
async def api_root():
    return {
        "status": "success",
        "data": {
            "name": "Summit SEO API",
            "version": "1.0.0",
            "documentation": "/api/docs"
        }
    }

# Health check endpoint
@app.get("/api/v1/health", tags=["Health"])
async def health_check():
    return {
        "status": "success",
        "data": {
            "status": "healthy",
            "timestamp": time.time()
        }
    }

# Custom OpenAPI schema
def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    
    openapi_schema = get_openapi(
        title="Summit SEO API",
        version="1.0.0",
        description="REST API for Summit SEO web application",
        routes=app.routes,
    )
    
    # Customize the schema here if needed
    
    app.openapi_schema = openapi_schema
    return app.openapi_schema

app.openapi = custom_openapi 