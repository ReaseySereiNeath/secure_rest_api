from slowapi import Limiter
from slowapi.util import get_remote_address
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware

# limiter = Limiter(key_func=get_remote_address)
# Default: 5 requests per minute per IP
limiter = Limiter(key_func=get_remote_address, default_limits=["5/minute"])

def register_rate_limiter(app: FastAPI):
    app.state.limiter = limiter
    app.add_middleware(SlowAPIMiddleware)

    @app.exception_handler(RateLimitExceeded)
    async def rate_limit_exceeded(request: Request, exc: RateLimitExceeded):
        return JSONResponse(status_code=429, content={"detail": "Too many requests"})
