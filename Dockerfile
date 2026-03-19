# Stage 1: Install dependencies
FROM python:3.12-slim AS builder
WORKDIR /build
COPY pyproject.toml .
COPY plugindb/ plugindb/
RUN pip install --no-cache-dir --prefix=/install .

# Stage 2: Seed the database
FROM python:3.12-slim AS seeder
COPY --from=builder /install /usr/local
WORKDIR /app
COPY plugindb/ plugindb/
COPY data/seed.json data/seed.json
RUN python -m plugindb.seed

# Stage 3: Runtime
FROM python:3.12-slim
COPY --from=builder /install /usr/local
COPY --from=seeder /app /app
WORKDIR /app
COPY frontend/ frontend/

RUN useradd --create-home plugindb
USER plugindb

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
  CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/health')" || exit 1

CMD ["uvicorn", "plugindb.main:create_app", "--factory", "--host", "0.0.0.0", "--port", "8000"]
