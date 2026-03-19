FROM python:3.12-slim
WORKDIR /app
COPY pyproject.toml .
RUN pip install --no-cache-dir .
COPY . .
RUN python -m plugindb.seed
EXPOSE 8000
CMD ["uvicorn", "plugindb.main:create_app", "--factory", "--host", "0.0.0.0", "--port", "8000"]
