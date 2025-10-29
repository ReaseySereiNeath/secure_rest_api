# ---------- Base Image ----------
FROM python:3.10-slim AS base

# ---------- Set working directory ----------
WORKDIR /app

# ---------- Environment Variables ----------
# Prevent Python from writing pyc files and buffer logs
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# ---------- Install dependencies ----------
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && pip install --no-cache-dir -r requirements.txt

# ---------- Copy Application Code ----------
COPY . .

# ---------- Optional Environment Config ----------
# Control whether Alembic migrations should run at startup
ENV RUN_MIGRATIONS=true
# Optional seed flag for initial admin data
ENV RUN_SEED=false

# Expose FastAPI port
EXPOSE 8000

# ---------- Startup Command ----------
# Copy entrypoint script
COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

# Use JSON format for CMD
CMD ["./entrypoint.sh"]
