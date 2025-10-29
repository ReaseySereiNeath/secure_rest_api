#!/bin/bash
set -e  # Exit immediately on error

echo "Starting container setup..."

# ---------- 1. Run Alembic migrations ----------
if [ "$RUN_MIGRATIONS" = "true" ]; then
  echo "Running Alembic migrations..."
  alembic upgrade head
  echo "Alembic migrations complete."
else
  echo "Skipping migrations (RUN_MIGRATIONS=$RUN_MIGRATIONS)"
fi

# ---------- 2. Run optional seeding ----------
if [ "$RUN_SEED" = "true" ]; then
  echo "Running database seed..."
  python seed_data.py
  echo "Database seed complete."
else
  echo "Skipping seeding (RUN_SEED=$RUN_SEED)"
fi

# ---------- 3. Start FastAPI ----------
echo "Launching FastAPI app..."
exec uvicorn main:app --host 0.0.0.0 --port 8000
