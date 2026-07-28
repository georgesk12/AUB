
# ==========================================================================
# Builder stage: install dependencies into an isolated virtualenv.
# Kept separate so build-time pip/cache never lands in the runtime image.
# ==========================================================================
FROM python:3.12-slim AS builder

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

# Isolated venv; all deps installed here, wheels only, no cache.
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

# ==========================================================================
# Runtime stage: minimal image, runs as a non-root user.
# ==========================================================================
FROM python:3.12-slim AS runtime

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PATH="/opt/venv/bin:$PATH"

# Non-root user to run the app.
RUN useradd --create-home --uid 1000 app

WORKDIR /app

# Bring in the prebuilt virtualenv from the builder stage.
COPY --from=builder /opt/venv /opt/venv

# Copy ONLY the application code. Tests, docs, frontend, .env, .git, etc. are
# excluded here and via .dockerignore - the runtime image needs neither them
# nor any secret.
COPY --chown=app:app app ./app

EXPOSE 8000

# Drop privileges: everything below runs as 'app', not root.
USER app

# Container health check hits the app's own /health endpoint.
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD python -c "import urllib.request,sys; sys.exit(0 if urllib.request.urlopen('http://127.0.0.1:8000/health').status==200 else 1)"

# Production run: bind to 0.0.0.0 so the host can reach it; NO --reload.
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
