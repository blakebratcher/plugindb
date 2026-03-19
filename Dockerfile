FROM python:3.12-slim
WORKDIR /app
COPY pyproject.toml .
RUN pip install --no-cache-dir .
COPY . .
RUN python -m plugindb.seed

RUN useradd --create-home plugindb
USER plugindb

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
  CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/health')" || exit 1

CMD ["uvicorn", "plugindb.main:create_app", "--factory", "--host", "0.0.0.0", "--port", "8000"]
