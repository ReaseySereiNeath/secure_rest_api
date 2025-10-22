# middlewares/error_handler.py
import time
import logging
import traceback
from fastapi import Request
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware

error_logger = logging.getLogger("error_logger")

class ExceptionLoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        start_time = time.time()
        try:
            response = await call_next(request)
            return response

        except Exception as e:
            process_time = time.time() - start_time
            tb = traceback.format_exc()
            error_logger.error(
                f"Exception on {request.method} {request.url.path} | "
                f"{process_time:.2f}s | {repr(e)}\n{tb}"
            )

            # Optional: clean JSON error response
            return JSONResponse(
                status_code=500,
                content={"detail": "Internal Server Error"},
            )
