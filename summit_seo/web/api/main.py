from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
import logging
import time
import uuid
from typing import Dict, Any

# Import routers
from .routers import auth, users, projects, analyses, reports
from .core.config import settings
from .core.app import app as core_app

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger("summit-seo-api")

# Create FastAPI app
app = FastAPI(
    title=settings.PROJECT_NAME,
    description="REST API for Summit SEO analysis tool",
    version="1.0.0",
    openapi_url=f"{settings.API_V1_STR}/openapi.json"
)

# Set up CORS middleware
if settings.BACKEND_CORS_ORIGINS:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[str(origin) for origin in settings.BACKEND_CORS_ORIGINS],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

# Request ID middleware for tracking requests
@app.middleware("http")
async def add_request_id(request: Request, call_next):
    request_id = str(uuid.uuid4())
    request.state.request_id = request_id
    
    # Add request ID to response headers
    response = await call_next(request)
    response.headers["X-Request-ID"] = request_id
    
    return response

# Logging middleware
@app.middleware("http")
async def log_requests(request: Request, call_next):
    start_time = time.time()
    
    # Get request details
    method = request.method
    url = request.url.path
    
    # Get request ID from state (set by previous middleware)
    request_id = getattr(request.state, "request_id", "unknown")
    
    # Log request
    logger.info(f"Request {request_id} started: {method} {url}")
    
    # Process request
    response = await call_next(request)
    
    # Calculate processing time
    process_time = time.time() - start_time
    
    # Log response
    logger.info(f"Request {request_id} completed: {response.status_code} ({process_time:.4f}s)")
    
    return response

# Custom error handler for validation errors
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    errors = []
    for error in exc.errors():
        error_detail = {
            "loc": error["loc"],
            "msg": error["msg"],
            "type": error["type"],
        }
        errors.append(error_detail)
    
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "status": "error",
            "error": {
                "code": "VALIDATION_ERROR",
                "message": "Validation error",
                "details": {"errors": errors}
            }
        },
    )

# Health check endpoint
@app.get("/health")
def health_check():
    return {
        "status": "success",
        "data": {
            "service": "summit-seo-api",
            "version": "1.0.0",
            "healthy": True
        },
        "meta": None
    }

# Include routers
app.include_router(auth.router, prefix=f"{settings.API_V1_STR}/auth", tags=["auth"])
app.include_router(users.router, prefix="/users", tags=["Users"])
app.include_router(projects.router, prefix=f"{settings.API_V1_STR}/projects", tags=["projects"])
app.include_router(analyses.router, prefix=f"{settings.API_V1_STR}/projects/{{project_id}}/analyses", tags=["analyses"])
app.include_router(reports.router, prefix=f"{settings.API_V1_STR}/projects/{{project_id}}/reports", tags=["reports"])

# Mount core app
app.mount("/api", core_app)

@app.get("/")
async def root():
    return {
        "message": "Welcome to Summit SEO API",
        "version": settings.API_V1_STR,
        "docs_url": "/docs",
        "openapi_url": f"{settings.API_V1_STR}/openapi.json"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True) 