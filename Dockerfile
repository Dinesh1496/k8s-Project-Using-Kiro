# ─────────────────────────────────────────────
# Stage 1: Builder
# ─────────────────────────────────────────────
FROM python:3.12-slim AS builder

WORKDIR /build

# Install build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy and install Python dependencies into a prefix directory
COPY requirements.txt .
RUN pip install --upgrade pip \
    && pip install --prefix=/install --no-cache-dir -r requirements.txt


# ─────────────────────────────────────────────
# Stage 2: Runtime
# ─────────────────────────────────────────────
FROM python:3.12-slim AS runtime

LABEL maintainer="your-email@example.com"
LABEL org.opencontainers.image.title="flask-cicd-demo"
LABEL org.opencontainers.image.version="1.0.0"
LABEL org.opencontainers.image.description="Production Flask CI/CD Demo"

# Create non-root user and group
RUN groupadd --gid 1001 appgroup \
    && useradd --uid 1001 --gid appgroup --shell /bin/bash --create-home appuser

WORKDIR /app

# Copy installed packages from builder stage
COPY --from=builder /install /usr/local

# Copy application source
COPY --chown=appuser:appgroup app.py .

# Switch to non-root user
USER appuser

# Expose application port
EXPOSE 5000

# Healthcheck — calls the /health endpoint every 30s
HEALTHCHECK --interval=30s --timeout=10s --start-period=15s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:5000/health')" || exit 1

# Run with Gunicorn (production WSGI server)
CMD ["gunicorn", \
     "--bind", "0.0.0.0:5000", \
     "--workers", "2", \
     "--threads", "2", \
     "--timeout", "60", \
     "--access-logfile", "-", \
     "--error-logfile", "-", \
     "--log-level", "info", \
     "app:app"]
