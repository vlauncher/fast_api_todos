# ---------- Builder Stage ----------
FROM python:3.11-slim AS builder
WORKDIR /app

# Install build deps
RUN apt-get update \
 && apt-get install -y --no-install-recommends gcc libpq-dev \
 && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --upgrade pip \
 && pip wheel --no-cache-dir --no-deps --wheel-dir /app/wheels -r requirements.txt

# ---------- Runtime Stage ----------
FROM python:3.11-slim AS runtime
WORKDIR /app

# System dependencies
RUN apt-get update \
 && apt-get install -y --no-install-recommends \
    libpq5 \
    curl \
    supervisor \
 && rm -rf /var/lib/apt/lists/*

# Install wheels
COPY --from=builder /app/wheels /wheels
RUN pip install --no-cache /wheels/*

# Copy code
COPY . .

# Add supervisord config
COPY supervisord.conf /etc/supervisor/conf.d/supervisord.conf

# Expose port
EXPOSE 8000



# Run supervisord to manage FastAPI + Celery
CMD ["supervisord", "-c", "/etc/supervisor/conf.d/supervisord.conf"]
