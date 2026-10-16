"""Alembic environment: runs the migrations with the same URL the service uses (RQ_DATABASE_URL)."""

import asyncio

from alembic import context
from refresquito_fastapi import Settings
from refresquito_fastapi.db import Base
from sqlalchemy.ext.asyncio import create_async_engine

import ${{ values.name }}.models  # noqa: F401  (registers the tables in Base.metadata)

target_metadata = Base.metadata


def url() -> str:
    value = context.get_x_argument(as_dictionary=True).get("url") or Settings().database_url
    if not value:
        raise SystemExit("Set RQ_DATABASE_URL (or pass -x url=...)")
    return value


def run(connection) -> None:
    context.configure(connection=connection, target_metadata=target_metadata, compare_type=True)
    with context.begin_transaction():
        context.run_migrations()


async def online() -> None:
    engine = create_async_engine(url())
    async with engine.connect() as connection:
        await connection.run_sync(run)
    await engine.dispose()


if context.is_offline_mode():
    context.configure(url=url(), target_metadata=target_metadata, literal_binds=True)
    with context.begin_transaction():
        context.run_migrations()
else:
    asyncio.run(online())
