# ${{ values.title }} API. Build from the root of the repository:  podman build -f backend/Dockerfile .
FROM docker.io/library/python:3.12-slim AS build
WORKDIR /src
COPY vendor ./vendor
COPY backend/pyproject.toml ./backend/
COPY backend/src ./backend/src
RUN pip install --no-cache-dir --find-links vendor --prefix=/install ./backend

FROM docker.io/library/python:3.12-slim
RUN useradd --uid 10001 --no-create-home ${{ values.name }}
COPY --from=build /install /usr/local
WORKDIR /app
COPY backend/alembic.ini ./
COPY backend/migrations ./migrations
USER 10001
EXPOSE 8000
ENV RQ_APP_NAME=${{ values.name }}
# migrate, then serve: with one replica the migration needs no lock of its own
CMD ["sh", "-c", "alembic upgrade head && exec uvicorn ${{ values.name }}.main:app --host 0.0.0.0 --port 8000 --no-access-log"]
