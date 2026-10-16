"""Tests run against a real PostgreSQL, with the schema the migrations create.

Start one with `podman compose up -d db` (or docker) at the root of the repository, or point
RQ_TEST_DATABASE_URL at another one. Every test starts with empty tables.
"""

import os
import subprocess
import sys
from pathlib import Path

import pytest
from refresquito_fastapi import Settings
from refresquito_fastapi.db import Base, Database
from refresquito_fastapi.testing import (
    FakeDocuments,
    FakeFlows,
    FakeProcesses,
    FakeStorage,
    TokenFactory,
    client_for,
    platform_with,
)
from sqlalchemy import text

from ${{ values.name }}.main import build

BACKEND = Path(__file__).resolve().parent.parent
URL = os.environ.get("RQ_TEST_DATABASE_URL", "postgresql+asyncpg://${{ values.name }}:${{ values.name }}@localhost:55432/app_test")


@pytest.fixture
def anyio_backend() -> str:
    return "asyncio"


@pytest.fixture(scope="session")
def migrated() -> str:
    """The test database, emptied and brought to the latest migration once per run."""

    def alembic(*args: str) -> None:
        subprocess.run([sys.executable, "-m", "alembic", "-x", f"url={URL}", *args], cwd=BACKEND, check=True)

    alembic("downgrade", "base")
    alembic("upgrade", "head")
    return URL


@pytest.fixture
async def database(migrated):
    db = Database(migrated)
    async with db.engine.begin() as connection:
        # quoted: a table may be named like a reserved word of SQL (order, user, group)
        tables = ", ".join(f'"{t.name}"' for t in Base.metadata.sorted_tables)
        await connection.execute(text(f"TRUNCATE {tables} RESTART IDENTITY CASCADE"))
    yield db
    await db.dispose()


@pytest.fixture(scope="session")
def tokens() -> TokenFactory:
    return TokenFactory()


@pytest.fixture
def processes() -> FakeProcesses:
    fake = FakeProcesses(key_prefix="${{ values.name }}-")
    fake.deploy("review", tasks=["review"])   # platform/processes/${{ values.name }}-review.bpmn: one user task
    return fake


@pytest.fixture
def flows() -> FakeFlows:
    return FakeFlows({"new-${{ values.entity }}": {"message": "Welcome!"}})


@pytest.fixture
def storage() -> FakeStorage:
    return FakeStorage(["${{ values.buckets[0] if values.buckets | length else 'files' }}"], app="${{ values.name }}")


@pytest.fixture
def documents() -> FakeDocuments:
    return FakeDocuments(["${{ values.sites[0] if values.sites | length else 'documents' }}"], app="${{ values.name }}")


# the platform blocks it declares (its file in refresquito-services), each one in memory: the fixtures above
PLATFORM_BLOCKS = [
{%- if values.processes %}
    "processes",  # block processes
{%- endif %}
{%- if values.flows %}
    "flows",  # block flows
{%- endif %}
{%- if (values.buckets | length) > 0 %}
    "storage",  # block s3
{%- endif %}
{%- if (values.sites | length) > 0 %}
    "documents",  # block dms
{%- endif %}
]


@pytest.fixture
async def client(database, tokens, request):
    platform = platform_with(*(request.getfixturevalue(name) for name in PLATFORM_BLOCKS))
    app = build(Settings(app_name="${{ values.name }}"), token_verifier=tokens.verifier(), database=database, platform=platform)
    async with client_for(app) as c:
        yield c


@pytest.fixture
def admin(tokens) -> dict[str, str]:
    return tokens.headers("ana", roles=["${{ values.name }}-admin"])


@pytest.fixture
def viewer(tokens) -> dict[str, str]:
    return tokens.headers("luis", roles=["${{ values.name }}-viewer"])
