FROM python:3.14-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Install nginx
RUN apt-get update \
    && apt-get install -y nginx \
    && rm -rf /var/lib/apt/lists/*

# Install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# Install Python dependencies
COPY pyproject.toml uv.lock ./

RUN uv sync --frozen --no-dev

# Copy backend application
COPY agent ./agent
COPY backend ./backend
COPY data ./data
COPY model ./model

# Copy frontend
COPY frontend/index.html /usr/share/nginx/html/
COPY frontend/script.js /usr/share/nginx/html/
COPY frontend/style.css /usr/share/nginx/html/

# Copy nginx configuration
COPY frontend/nginx.conf /etc/nginx/conf.d/default.conf

# Render will expose this port
EXPOSE 10000

# Start FastAPI and nginx
CMD ["sh", "-c", "uv run uvicorn backend.main:app --host 0.0.0.0 --port 8000 & nginx -g 'daemon off;'"]