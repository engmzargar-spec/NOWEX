import logging
import traceback
from fastapi import Request, HTTPException
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from sqlalchemy.exc import SQLAlchemyError

from ..exceptions import (
    NOWEXException,
    AuthenticationError,
    AuthorizationError,
    ScoringError,
    ReferralError,
    KYCError,
    DatabaseError,
    ValidationError,
    NotFoundError,
    ExternalServiceError
)

logger = logging.getLogger("error_handler")

async def nowex_exception_handler(request: Request, exc: NOWEXException):
    """Handler for custom NOWEX exceptions"""
    logger.warning(
        f"NOWEX Exception: {exc.code} - {exc.message}",
        extra={
            "status_code": exc.status_code,
            "path": request.url.path,
            "method": request.method,
            "error_code": exc.code
        }
    )
    
    response_data = {
        "error": {
            "code": exc.code,
            "message": exc.message,
            "status_code": exc.status_code
        }
    }
    
    # اضافه کردن جزئیات بیشتر اگر وجود دارد
    if hasattr(exc, 'details') and exc.details:
        response_data["error"]["details"] = exc.details
    
    if hasattr(exc, 'field') and exc.field:
        response_data["error"]["field"] = exc.field
    
    return JSONResponse(
        status_code=exc.status_code,
        content=response_data
    )

async def http_exception_handler(request: Request, exc: HTTPException):
    """Handler for FastAPI HTTP exceptions"""
    logger.warning(
        f"HTTP Exception: {exc.status_code} - {exc.detail}",
        extra={
            "status_code": exc.status_code,
            "path": request.url.path,
            "method": request.method
        }
    )
    
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": {
                "code": "HTTP_ERROR",
                "message": exc.detail,
                "status_code": exc.status_code
            }
        }
    )

async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Handler for request validation errors"""
    errors = []
    for error in exc.errors():
        errors.append({
            "field": " -> ".join(str(loc) for loc in error["loc"]),
            "message": error["msg"],
            "type": error["type"]
        })
    
    logger.warning(
        f"Validation Error: {len(errors)} errors",
        extra={
            "path": request.url.path,
            "method": request.method,
            "errors": errors
        }
    )
    
    return JSONResponse(
        status_code=422,
        content={
            "error": {
                "code": "VALIDATION_ERROR",
                "message": "Request validation failed",
                "status_code": 422,
                "details": errors
            }
        }
    )

async def database_exception_handler(request: Request, exc: SQLAlchemyError):
    """Handler for database errors"""
    logger.error(
        f"Database Error: {str(exc)}",
        extra={
            "path": request.url.path,
            "method": request.method,
            "error_type": exc.__class__.__name__
        },
        exc_info=True
    )
    
    return JSONResponse(
        status_code=500,
        content={
            "error": {
                "code": "DATABASE_ERROR",
                "message": "Database operation failed",
                "status_code": 500
            }
        }
    )

async def generic_exception_handler(request: Request, exc: Exception):
    """Handler for all other unhandled exceptions"""
    logger.error(
        f"Unhandled Exception: {str(exc)}",
        extra={
            "path": request.url.path,
            "method": request.method,
            "error_type": exc.__class__.__name__
        },
        exc_info=True
    )
    
    # در محیط production پیام کلی نشان داده شود
    error_message = "Internal server error"
    if hasattr(request.app, "debug") and request.app.debug:
        error_message = f"Unhandled error: {str(exc)}"
    
    return JSONResponse(
        status_code=500,
        content={
            "error": {
                "code": "INTERNAL_ERROR",
                "message": error_message,
                "status_code": 500
            }
        }
    )

def setup_exception_handlers(app):
    """Setup all exception handlers for the FastAPI app"""
    
    # NOWEX custom exceptions
    app.add_exception_handler(NOWEXException, nowex_exception_handler)
    app.add_exception_handler(AuthenticationError, nowex_exception_handler)
    app.add_exception_handler(AuthorizationError, nowex_exception_handler)
    app.add_exception_handler(ScoringError, nowex_exception_handler)
    app.add_exception_handler(ReferralError, nowex_exception_handler)
    app.add_exception_handler(KYCError, nowex_exception_handler)
    app.add_exception_handler(DatabaseError, nowex_exception_handler)
    app.add_exception_handler(ValidationError, nowex_exception_handler)
    app.add_exception_handler(NotFoundError, nowex_exception_handler)
    app.add_exception_handler(ExternalServiceError, nowex_exception_handler)
    
    # FastAPI and standard exceptions
    app.add_exception_handler(HTTPException, http_exception_handler)
    app.add_exception_handler(RequestValidationError, validation_exception_handler)
    app.add_exception_handler(SQLAlchemyError, database_exception_handler)
    
    # Generic exception handler (should be last)
    app.add_exception_handler(Exception, generic_exception_handler)
    
    logger.info("✅ Exception handlers setup completed")