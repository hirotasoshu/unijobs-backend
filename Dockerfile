FROM python:3.12-slim AS runtime

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app \
    POETRY_VERSION=2.4.1

WORKDIR /app

RUN pip install --no-cache-dir "poetry==$POETRY_VERSION"

COPY pyproject.toml poetry.lock ./
RUN poetry config virtualenvs.create false \
    && poetry install --only main --no-interaction --no-ansi

COPY alembic.ini ./
COPY migrations ./migrations
COPY scripts ./scripts
COPY src ./src

EXPOSE 8080

CMD ["uvicorn", "src.presentation.http.app:create_app", "--factory", "--host", "0.0.0.0", "--port", "8080"]
