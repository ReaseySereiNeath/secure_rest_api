from slowapi import Limiter
from slowapi.util import get_remote_address
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware
from config import DEFAULT_RATE_LIMIT

# limiter = Limiter(key_func=get_remote_address)
# Default: 5 requests per minute per IP
limiter = Limiter(key_func=get_remote_address, default_limits=[DEFAULT_RATE_LIMIT])

def register_rate_limiter(app: FastAPI):
    app.state.limiter = limiter
    app.add_middleware(SlowAPIMiddleware)

    @app.exception_handler(RateLimitExceeded)
    async def rate_limit_exceeded(request: Request, exc: RateLimitExceeded):
        retry_after = None
        if isinstance(getattr(exc, "headers", None), dict):
            retry_after = exc.headers.get("Retry-After")
        elif hasattr(request.state, "view_rate_limit"):
            reset_in = getattr(request.state.view_rate_limit, "reset_in", None)
            if reset_in is not None:
                try:
                    retry_after = str(max(0, int(reset_in)))
                except (TypeError, ValueError):
                    retry_after = str(reset_in)

        headers = {"Retry-After": str(retry_after)} if retry_after is not None else {}
        return JSONResponse(
            status_code=429,
            content={"detail": "Too many requests. Try again later."},
            headers=headers,
        )
