from contextlib import asynccontextmanager
import logging
import time
import uuid
from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.database import (
    engine,
    Base,
    check_database_connection,
    verify_database_schema,
    safe_initialize_database,
)
from app.routers import (
    health,
    auth,
    complaints,
    notifications,
    management,
    faculty,
    intelligence,
    academics,
    alerts,
    career,
    career_management,
    viit,
    insights,
    actions,
)
import app.models  # Register all models

# Configure Structured Logging
logging.basicConfig(
    level=getattr(logging, settings.LOG_LEVEL.upper(), logging.INFO),
    format="%(asctime)s [%(levelname)s] [%(name)s] %(message)s",
)
logger = logging.getLogger("vignai_os")


@asynccontextmanager
async def lifespan(app: FastAPI):
    # 1. Validate Environment & Secrets
    logger.info("Initializing VIGNAI OS in environment: %s", settings.ENVIRONMENT)
    settings.validate_production_readiness()

    # 2. Database Connectivity & Safe Multi-Worker Schema Verification
    logger.info("Verifying database connectivity...")
    if not check_database_connection():
        logger.warning("Database connection ping failed on startup; will retry on incoming requests.")
    else:
        logger.info("Database connection established.")

    if verify_database_schema():
        logger.info("Database schema and migrations verified (tables present). Skipping redundant worker DDL.")
    else:
        logger.info("Database schema missing or incomplete. Initializing safely across workers...")
        safe_initialize_database()
        logger.info("Database schema and migrations verified.")

    # 3. Demo Seeding Check
    from app.database import SessionLocal
    from app.models.user import User
    db = SessionLocal()
    try:
        user_count = db.query(User).count()
        if user_count == 0 or settings.ENABLE_DEMO_SEEDING:
            if user_count == 0:
                logger.info("Database has 0 users. Initializing default accounts via official seed pipeline...")
                from app.seed import run_seed
                run_seed()
                logger.info("Default demo accounts seeded successfully.")
            else:
                logger.info("Database already populated with %d users. Skipping redundant seed.", user_count)
    except Exception as seed_err:
        logger.error("Demo seeding check error: %s", seed_err, exc_info=True)
    finally:
        db.close()

    yield

    logger.info("Shutting down VIGNAI OS...")


# Configure FastAPI application
app = FastAPI(
    title="VIGNAI OS API",
    description="Vignan's AI Campus Operating System",
    version="1.0.0",
    docs_url=None if settings.is_production else "/docs",
    redoc_url=None if settings.is_production else "/redoc",
    openapi_url=None if settings.is_production else "/openapi.json",
    lifespan=lifespan,
)

# Production CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)


# Structured Request / Response Logging Middleware
@app.middleware("http")
async def structured_logging_middleware(request: Request, call_next):
    start_time = time.time()
    request_id = uuid.uuid4().hex[:8]
    request.state.request_id = request_id

    # Mask sensitive headers in logs
    path = request.url.path
    method = request.method
    client_host = request.client.host if request.client else "unknown"

    try:
        response = await call_next(request)
        duration_ms = round((time.time() - start_time) * 1000, 2)
        response.headers["X-Request-ID"] = request_id

        # Log non-health requests or errors
        if not path.endswith("/health") or response.status_code >= 400:
            logger.info(
                "[%s] %s %s -> %s (%sms) from %s",
                request_id,
                method,
                path,
                response.status_code,
                duration_ms,
                client_host,
            )
        return response
    except Exception as exc:
        duration_ms = round((time.time() - start_time) * 1000, 2)
        logger.error(
            "[%s] %s %s EXCEPTION after %sms: %s",
            request_id,
            method,
            path,
            duration_ms,
            exc,
            exc_info=True,
        )
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "detail": "An unexpected internal server error occurred.",
                "request_id": request_id,
            },
            headers={"X-Request-ID": request_id},
        )


# Global Unhandled Exception Handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    req_id = getattr(request.state, "request_id", uuid.uuid4().hex[:8])
    logger.error("[%s] Unhandled Exception: %s", req_id, exc, exc_info=True)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "detail": "An internal server error occurred.",
            "request_id": req_id,
        },
        headers={"X-Request-ID": req_id},
    )


# Mount Root and API Health Endpoints
app.include_router(health.router)                 # Accessible at GET /health
app.include_router(health.router, prefix="/api")  # Accessible at GET /api/health

# Application Routers under /api
app.include_router(auth.router, prefix="/api")
app.include_router(complaints.router, prefix="/api")
app.include_router(notifications.router, prefix="/api")
app.include_router(management.router, prefix="/api")
app.include_router(faculty.router, prefix="/api")
app.include_router(intelligence.router, prefix="/api")
app.include_router(academics.router, prefix="/api")
app.include_router(alerts.router, prefix="/api")
app.include_router(viit.router, prefix="/api")
app.include_router(insights.router, prefix="/api")
app.include_router(actions.router, prefix="/api")
app.include_router(career.router)
app.include_router(career_management.router)
