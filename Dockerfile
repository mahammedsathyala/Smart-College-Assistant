# ============================================================
# Smart College Assistant — Production Dockerfile
# Multi-stage build for lean production image
# ============================================================

# ── Stage 1: Build dependencies ─────────────────────────────
FROM python:3.11-slim AS builder

WORKDIR /build

# Install build tools
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential gcc \
    && rm -rf /var/lib/apt/lists/*

# Install Python deps
COPY requirements.txt .
RUN pip install --user --no-cache-dir -r requirements.txt

# ── Stage 2: Production image ────────────────────────────────
FROM python:3.11-slim AS production

# Labels
LABEL maintainer="Smart College AI Team"
LABEL version="2.0.0"
LABEL description="Smart College Assistant — AI-powered College Platform"

# Create non-root user
RUN groupadd -r smartcollege && useradd -r -g smartcollege smartcollege

WORKDIR /app

# Install runtime dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    libgomp1 \
    && rm -rf /var/lib/apt/lists/*

# Copy installed packages from builder
COPY --from=builder /root/.local /home/smartcollege/.local

# Copy application
COPY --chown=smartcollege:smartcollege . .

# Create required directories
RUN mkdir -p /app/data /app/uploads /app/vectorstore /app/logs /app/flask_sessions \
    && chown -R smartcollege:smartcollege /app

# Switch to non-root
USER smartcollege

# Environment
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PATH=/home/smartcollege/.local/bin:$PATH \
    FLASK_ENV=production \
    PORT=5000 \
    HOST=0.0.0.0

# Expose port
EXPOSE 5000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:5000/api/health')" || exit 1

# Startup command (gunicorn for production)
CMD ["python", "-m", "gunicorn", \
     "--workers", "2", \
     "--threads", "4", \
     "--bind", "0.0.0.0:5000", \
     "--timeout", "120", \
     "--access-logfile", "-", \
     "--error-logfile", "-", \
     "app:create_app()"]
