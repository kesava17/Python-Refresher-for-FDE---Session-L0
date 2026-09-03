# One image, three services. docker-compose runs it three times with a different command,
# which is the "one image per service" idea in the small: same build, different entry point.
FROM python:3.12-slim

WORKDIR /app
RUN pip install --no-cache-dir poetry

COPY pyproject.toml ./
RUN poetry config virtualenvs.create false && poetry install --only main --no-root

COPY src ./src
ENV PYTHONPATH=/app/src

# Overridden per service in docker-compose.yml.
CMD ["uvicorn", "gateway.main:app", "--host", "0.0.0.0", "--port", "8000"]
