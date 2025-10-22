import time 
import logging
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response
from starlette.middleware.errors import ServerErrorMiddleware
from dotenv import load_dotenv
import os
from logging.handlers import RotatingFileHandler
from jose import jwt, JWTError

load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")

# Create logs directory if missing
if not os.path.exists("logs"):
    os.makedirs("logs")

# --- Configure main access log ---
access_handler = RotatingFileHandler("logs/app.log", maxBytes=2_000_000, backupCount=5)
access_formatter = logging.Formatter(
    "%(asctime)s | %(levelname)s | %(message)s", "%Y-%m-%d %H:%M:%S"
)
access_handler.setFormatter(access_formatter)

access_logger = logging.getLogger("access_logger")
access_logger.setLevel(logging.INFO)
access_logger.addHandler(access_handler)

# --- Configure error log ---
error_handler = RotatingFileHandler("logs/error.log", maxBytes=2_000_000, backupCount=5)
error_formatter = logging.Formatter(
    "%(asctime)s | %(levelname)s | %(message)s", "%Y-%m-%d %H:%M:%S"
)
error_handler.setFormatter(error_formatter)

error_logger = logging.getLogger("error_logger")
error_logger.setLevel(logging.ERROR)
error_logger.addHandler(error_handler)
error_logger.propagate = False   # <- Important! prevents duplicate logs


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

            log_message = (
                f"{method} {path} | Status {response.status_code} | "
                f"User: {user} | {process_time:.2f}s"
            )

            if response.status_code >= 400:
                error_logger.error(log_message)
            else:
                access_logger.info(log_message)

            return response

        except Exception as e:
            process_time = time.time() - start_time
            error_message = (
                f"ERROR on {method} {path} | User: {user} | "
                f"{process_time:.2f}s | Exception: {repr(e)}"
            )
            error_logger.error(error_message)
            raise e