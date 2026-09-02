FROM python:3.14-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-dev

COPY agent ./agent
COPY backend ./backend
COPY data ./data
COPY model ./model
COPY frontend ./frontend

RUN apt-get update \
    && apt-get install -y nginx \
    && rm -rf /var/lib/apt/lists/*

COPY frontend/index.html /usr/share/nginx/html/
COPY frontend/script.js /usr/share/nginx/html/
COPY frontend/style.css /usr/share/nginx/html/
COPY frontend/nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 10000

CMD ["sh", "-c", "uv run uvicorn backend.main:app --host 127.0.0.1 --port 8000 & nginx -g 'daemon off;'"]