import traceback
import uuid
from contextlib import asynccontextmanager
from datetime import datetime, timezone
from time import time

from fastapi import FastAPI, Request, Response, status
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy import text

from app.config import settings
from app.core.exceptions import LoopsAPIException
from app.core.logging import logger, setup_logging
from app.database import engine
from app.api import router as api_router

# Track application start time for uptime calculation
APP_START_TIME = time()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan context manager for startup and shutdown events."""
    # Startup: Configure logging
    setup_logging()
    logger.info("Application starting", version=settings.app_version)

    yield

    # Shutdown: Dispose database engine
    logger.info("Application shutting down")
    await engine.dispose()


app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    debug=settings.debug,
    lifespan=lifespan,
)

# Middleware for request ID tracking
@app.middleware("http")
async def add_request_id_middleware(request: Request, call_next):
    """Add unique request ID to each request for tracking."""
    request_id = str(uuid.uuid4())
    request.state.request_id = request_id

    # Add request ID to logger context
    with logger.contextualize(request_id=request_id):
        logger.info(
            "Request started",
            method=request.method,
            path=request.url.path,
            client=request.client.host if request.client else None,
        )

        start_time = time()
        response = await call_next(request)
        duration = time() - start_time

        logger.info(
            "Request completed",
            method=request.method,
            path=request.url.path,
            status_code=response.status_code,
            duration_ms=round(duration * 1000, 2),
        )

        # Add request ID to response headers
        response.headers["X-Request-ID"] = request_id

        return response


# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Exception handlers
@app.exception_handler(LoopsAPIException)
async def loops_api_exception_handler(request: Request, exc: LoopsAPIException):
    """Handle custom Loops API exceptions."""
    request_id = getattr(request.state, "request_id", None)

    logger.error(
        "API exception occurred",
        error_type=exc.error_type,
        message=exc.message,
        status_code=exc.status_code,
        path=request.url.path,
        method=request.method,
        details=exc.details,
        request_id=request_id,
    )

    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": exc.error_type,
            "message": exc.message,
            **exc.details,
        },
        headers={"X-Request-ID": request_id} if request_id else {},
    )


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Handle Pydantic validation errors."""
    request_id = getattr(request.state, "request_id", None)

    errors = jsonable_encoder(exc.errors())

    logger.warning(
        "Validation error",
        method=request.method,
        path=request.url.path,
        errors=errors,
        request_id=request_id,
    )

    return JSONResponse(
        status_code=400,
        content={
            "error": "validation_error",
            "message": "Invalid request data",
            "details": errors,
        },
        headers={"X-Request-ID": request_id} if request_id else {},
    )


@app.exception_handler(Exception)
async def generic_exception_handler(request: Request, exc: Exception):
    """Handle all uncaught exceptions."""
    request_id = getattr(request.state, "request_id", None)

    # Log full traceback
    logger.exception(
        "Unhandled exception",
        exception_type=type(exc).__name__,
        exception_message=str(exc),
        path=request.url.path,
        method=request.method,
        request_id=request_id,
    )

    # Don't expose internal errors in production
    if settings.debug:
        return JSONResponse(
            status_code=500,
            content={
                "error": "internal_server_error",
                "message": str(exc),
                "traceback": traceback.format_exc(),
            },
            headers={"X-Request-ID": request_id} if request_id else {},
        )
    else:
        return JSONResponse(
            status_code=500,
            content={
                "error": "internal_server_error",
                "message": "An unexpected error occurred. Please try again later.",
            },
            headers={"X-Request-ID": request_id} if request_id else {},
        )


# Include API routes
app.include_router(api_router, prefix=settings.api_v1_prefix)


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "Welcome to Loops API",
        "version": settings.app_version,
        "docs": "/docs",
    }


@app.get("/health")
async def health(response: Response):
    """
    Health check endpoint.
    
    Tests database connectivity and returns service status.
    Returns 503 Service Unavailable if any critical component is unhealthy.
    """
    uptime_seconds = int(time() - APP_START_TIME)
    timestamp = datetime.now(timezone.utc).isoformat()
    
    health_status = {
        "status": "healthy",
        "version": settings.app_version,
        "uptime_seconds": uptime_seconds,
        "timestamp": timestamp,
        "database": "unknown"
    }
    
    # Test database connection
    try:
        async with engine.connect() as conn:
            await conn.execute(text("SELECT 1"))
            health_status["database"] = "connected"
    except Exception as e:
        health_status["status"] = "unhealthy"
        health_status["database"] = "disconnected"
        health_status["error"] = str(e)
        response.status_code = status.HTTP_503_SERVICE_UNAVAILABLE
    
    return health_status
