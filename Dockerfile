# syntax=docker/dockerfile:1

FROM python:3.11-slim AS runtime

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# Install OS packages minimally (add build deps only if needed)
RUN apt-get update \
  && apt-get install -y --no-install-recommends build-essential \
  && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Install Python dependencies first for better layer caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create an unprivileged user and set ownership (non-root best practice)
RUN useradd -m -u 10001 appuser && chown -R appuser:appuser /app
USER appuser

# Expose FastAPI/Uvicorn port
EXPOSE 8000

# Start the API; add --workers N for multi-worker if desired
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
