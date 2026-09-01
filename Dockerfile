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

EXPOSE 8000

CMD ["uv","run","uvicorn","backend.main:app","--host","0.0.0.0","--port","8000"]