# Base runtime
FROM python:3.11-slim

# Basics
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PORT=8080

WORKDIR /app

# System deps (keep minimal; add build-essential only if you compile)
# RUN apt-get update && apt-get install -y build-essential && rm -rf /var/lib/apt/lists/*

# 1) Install Python deps for the API (includes google-cloud-storage, torch, etc.)
COPY server/requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt && pip install gunicorn

# 2) Copy code: FastAPI service + your ml package code (so `from ml...` works)
COPY server /app/server
COPY ml /app/ml

# 3) Where we cache downloaded artifacts in the container
RUN mkdir -p /app/artifacts

# 4) Make repo root importable (so `ml/...` is on sys.path)
ENV PYTHONPATH=/app

EXPOSE 8080

# Gunicorn + Uvicorn worker (prod-grade)
CMD exec gunicorn server.app:app \
  -k uvicorn.workers.UvicornWorker \
  --bind 0.0.0.0:${PORT} \
  --workers 2 --threads 4 --timeout 120
