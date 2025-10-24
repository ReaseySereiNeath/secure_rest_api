# ---------- Base Image ----------
FROM python:3.10-slim

# ---------- Set working directory ----------
WORKDIR /app

# ---------- Install dependencies ----------
# Copy only the requirement files first (for caching)
COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

# ---------- Copy application code ----------
COPY . .

# ---------- Environment ----------
# Prevent Python from buffering stdout/stderr (so logs appear instantly)
ENV PYTHONUNBUFFERED=1

# Expose FastAPI port
EXPOSE 8000

# ---------- Command ----------
# Start the FastAPI server with uvicorn
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
