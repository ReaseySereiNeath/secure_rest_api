# SlowAPI Rate-Limiting Notes

## Problem
- Uvicorn crashed while importing `main.py` with `Exception: No "request" or "websocket" argument on function "<function ...>"`.
- Error triggered whenever `@limiter.limit(...)` decorated endpoints did not declare a `request` (or `websocket`) parameter.

## Root Cause
- SlowAPI’s decorator inspects the target signature at import time.
- Without a `Request` argument, SlowAPI cannot determine the client to rate-limit, so it raises an exception during application startup.

## Fix
1. Import `Request` from FastAPI:
   ```python
   from fastapi import FastAPI, Depends, HTTPException, status, Request
   ```
2. Update every rate-limited route to include `request: Request`, for example:
   ```python
   @app.post("/login")
   @limiter.limit("5/minute")
   def login(
       request: Request,
       form_data: OAuth2PasswordRequestForm = Depends(),
       db: Session = Depends(get_db),
   ):
       ...
   ```
3. Do the same wherever `@limiter.limit(...)` is applied (e.g. `get_items`).
4. Restart Uvicorn to confirm the service starts cleanly.

## Reference
- The limiter instance lives in `middlewares/rate_limit.py`.
- Middleware is registered in `main.py` via `register_rate_limiter(app)`.
