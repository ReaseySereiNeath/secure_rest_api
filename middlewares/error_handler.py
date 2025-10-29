# middlewares/error_handler.py
import time
import logging
import traceback
from fastapi import Request, HTTPException
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware

error_logger = logging.getLogger("error_logger")

class ExceptionLoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        start_time = time.time()
        try:
            response = await call_next(request)
            return response
        
        # Handle FastAPI-defined exceptions (e.g. 401, 404)
        except HTTPException as http_exc:
            process_time = time.time() - start_time
            request_id = getattr(request.state, "request_id", None)
            error_logger.error(
                f"HTTPException {http_exc.status_code} | {request.method} {request.url.path} | "
                f"Request ID: {request_id} | Detail: {http_exc.detail} | {process_time:.2f}s"
            )
            return JSONResponse(
                status_code=http_exc.status_code,
                content={
                    "detail": http_exc.detail,
                    "request_id": request_id
                },
                headers=http_exc.headers or {},
            )

        except Exception as e:
            process_time = time.time() - start_time
            tb = traceback.format_exc()
            request_id = getattr(request.state, "request_id", None)
            error_logger.error(
                f"Exception on {request.method} {request.url.path} | "
                f"Request ID: {request_id} | {process_time:.2f}s | {repr(e)}\n{tb}"
            )

            # Handle unexpected server errors (500)
            return JSONResponse(
                status_code=500,
                content={
                    "detail": "Internal Server Error", 
                    "request_id": request_id
                },
            )
