import logging
import os
import time
from logging.handlers import RotatingFileHandler

from dotenv import load_dotenv
from jose import JWTError, jwt
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

from middlewares.json_logger import JsonFormatter

env = os.getenv("ENV", "dev")
load_dotenv(f".env.{env}")

SECRET_KEY = os.getenv("SECRET_KEY", "")
ALGORITHM = os.getenv("ALGORITHM", "HS256")

if not os.path.exists("logs"):
    os.makedirs("logs")

json_formatter = JsonFormatter()

access_handler = RotatingFileHandler("logs/app.log", maxBytes=2_000_000, backupCount=5)
access_handler.setFormatter(json_formatter)

error_handler = RotatingFileHandler("logs/error.log", maxBytes=2_000_000, backupCount=5)
error_handler.setFormatter(json_formatter)

access_logger = logging.getLogger("access_logger")
access_logger.setLevel(logging.INFO)
access_logger.propagate = False
if not access_logger.handlers:
    access_logger.addHandler(access_handler)

error_logger = logging.getLogger("error_logger")
error_logger.setLevel(logging.ERROR)
error_logger.propagate = False
if not error_logger.handlers:
    error_logger.addHandler(error_handler)

class LoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        start_time = time.time()
        method = request.method
        path = request.url.path
        user = "anonymous"

        # Skip sensitive routes (login/register)
        if path in ["/login", "/register"]:
            response = await call_next(request)
            return response

        # Decode JWT for username
        auth_header = request.headers.get("Authorization")
        if auth_header and auth_header.startswith("Bearer "):
            token = auth_header.split(" ")[1]
            try:
                payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
                user = payload.get("sub", "unknown")
            except JWTError:
                user = "invalid_token"

        try:
            response: Response = await call_next(request)
            process_time = time.time() - start_time
            log_fields = {
                "user": user,
                "path": path,
                "method": method,
                "status_code": response.status_code,
                "process_time": round(process_time, 4),
            }

            if response.status_code >= 400:
                error_logger.error("request_completed", extra=log_fields)
            else:
                access_logger.info("request_completed", extra=log_fields)

            return response

        except Exception as e:
            process_time = time.time() - start_time
            error_fields = {
                "user": user,
                "path": path,
                "method": method,
                "status_code": 500,
                "process_time": round(process_time, 4),
                "exception": repr(e),
            }
            error_logger.error("request_failed", extra=error_fields)
            raise e
