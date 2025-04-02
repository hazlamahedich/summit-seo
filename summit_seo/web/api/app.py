from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.utils import get_openapi
import logging
from typing import Dict, Any, Optional, List

# Import routers
from .routers import auth, users, projects, analyses, settings, system, llm

# Import custom middleware
from .core.middleware import SupabaseAuthMiddleware
from .core.config import settings as app_settings
from .core.logging import configure_logging
from .core.error_handlers import configure_error_handlers

# Configure logging
configure_logging()
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title=app_settings.APP_NAME,
    description=app_settings.APP_DESCRIPTION,
    version=app_settings.APP_VERSION,
    openapi_url=f"{app_settings.API_V1_STR}/openapi.json",
    docs_url=f"{app_settings.API_V1_STR}/docs",
    redoc_url=f"{app_settings.API_V1_STR}/redoc",
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=app_settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add Supabase Authentication Middleware
app.add_middleware(
    SupabaseAuthMiddleware,
    public_paths=[
        "/api/docs",
        "/api/redoc",
        "/api/openapi.json",
        "/api/v1/auth/register",
        "/api/v1/auth/login",
        "/api/v1/auth/refresh",
        "/api/v1/auth/password-reset-request",
        "/api/v1/health",
    ]
)

# Configure error handling middleware and exception handlers
configure_error_handlers(app)

# Include routers
app.include_router(auth.router, prefix=app_settings.API_V1_STR)
app.include_router(users.router, prefix=app_settings.API_V1_STR)
app.include_router(projects.router, prefix=app_settings.API_V1_STR)
app.include_router(analyses.router, prefix=app_settings.API_V1_STR)
app.include_router(settings.router, prefix=app_settings.API_V1_STR)
app.include_router(system.router, prefix=app_settings.API_V1_STR)
app.include_router(llm.router, prefix=app_settings.API_V1_STR)

# Root endpoint
@app.get("/")
async def root():
    """Root endpoint that redirects to API documentation."""
    return {
        "name": app_settings.APP_NAME,
        "version": app_settings.APP_VERSION,
        "description": app_settings.APP_DESCRIPTION,
        "documentation": f"{app_settings.API_V1_STR}/docs"
    }

# Health check endpoint
@app.get("/health")
async def health():
    """Health check endpoint."""
    return {"status": "ok"}

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