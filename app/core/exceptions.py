# [Revisión] Ver CHANGELOG_REVISION.md -> "app/core/exceptions.py"
from datetime import datetime
from typing import Any, Dict, Optional
from fastapi import Request, HTTPException, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from app.core.logger import logger


def _build_error_response(
    error_type: str,
    code: int,
    message: str,
    details: Optional[Any] = None,
    path: Optional[str] = None,
) -> Dict[str, Any]:
    """Construye respuesta de error consistente para el frontend."""
    response = {
        "error": {
            "type": error_type,
            "code": code,
            "message": message,
            "timestamp": datetime.utcnow().isoformat() + "Z",
        }
    }
    if details:
        response["error"]["details"] = details
    if path:
        response["error"]["path"] = path
    return response


async def http_exception_handler(request: Request, exc: HTTPException):
    """Maneja excepciones HTTP controladas (401, 403, 404, etc.)."""
    logger.warning(
        f"HTTPException {exc.status_code} at {request.method} {request.url.path}: {exc.detail}"
    )
    
    error_type_map = {
        400: "BadRequest",
        401: "Unauthorized",
        403: "Forbidden",
        404: "NotFound",
        409: "Conflict",
        422: "ValidationError",
    }
    
    error_type = error_type_map.get(exc.status_code, "HTTPError")
    
    return JSONResponse(
        status_code=exc.status_code,
        content=_build_error_response(
            error_type=error_type,
            code=exc.status_code,
            message=exc.detail,
            path=request.url.path,
        ),
    )


async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Maneja errores de validación de Pydantic (422)."""
    errors = exc.errors()
    logger.warning(
        f"ValidationError at {request.method} {request.url.path}: {len(errors)} error(s)"
    )
    
    formatted_errors = []
    for error in errors:
        field = " -> ".join(str(loc) for loc in error["loc"])
        formatted_errors.append({
            "field": field,
            "message": error["msg"],
            "type": error["type"],
        })
    
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content=_build_error_response(
            error_type="ValidationError",
            code=422,
            message="Validation failed",
            details=formatted_errors,
            path=request.url.path,
        ),
    )


async def generic_exception_handler(request: Request, exc: Exception):
    """Maneja errores inesperados (500)."""
    logger.error(
        f"Unhandled exception at {request.method} {request.url.path}: {type(exc).__name__}",
        exc_info=True,
    )
    
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content=_build_error_response(
            error_type="InternalServerError",
            code=500,
            message="An unexpected error occurred. Please try again later.",
            path=request.url.path,
        ),
    )
