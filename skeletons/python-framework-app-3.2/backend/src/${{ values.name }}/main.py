"""The application: uvicorn ${{ values.name }}.main:app"""

from typing import Any

from fastapi import FastAPI
from refresquito_fastapi import Settings, create_app

from . import __version__
from .api import {% if values.flows %}ADMIN, VIEWER, {% endif %}router
{%- if values.dashboards %}
from .dashboards import router as dashboards_router
{%- endif %}
{%- if (values.sites | length) > 0 %}
from .documents import router as documents_router
{%- endif %}
{%- if (values.buckets | length) > 0 %}
from .files import router as files_router
{%- endif %}
{%- if values.processes %}
from .review import router as review_router
{%- endif %}
{%- if values.flows %}
from .welcome import router as welcome_router
{%- endif %}


def build(settings: Settings | None = None, **options: Any) -> FastAPI:
    # options: the other keyword arguments of create_app (the tests pass a verifier or a platform)
    settings = settings or Settings(app_name="${{ values.name }}")
    return create_app(
        settings,
        title="${{ values.title }} API",
        version=__version__,
        routers=[
            router,
            # what it does with the platform blocks it declares, one module each
{%- if values.processes %}
            review_router,  # block processes
{%- endif %}
{%- if values.flows %}
            welcome_router,  # block flows
{%- endif %}
{%- if (values.buckets | length) > 0 %}
            files_router,  # block s3
{%- endif %}
{%- if (values.sites | length) > 0 %}
            documents_router,  # block dms
{%- endif %}
{%- if values.dashboards %}
            dashboards_router,  # block dashboards
{%- endif %}
        ],
{%- if values.flows %}
        flow_runs=(VIEWER, ADMIN),  # block flows: the runs of its flows, GET /api/flow-runs
{%- endif %}
        docs_url="/api/docs",
        openapi_url="/api/openapi.json",
        **options,
    )


def __getattr__(name: str):
    # built on first use, so importing this module (tests, tools) does not need the environment
    if name == "app":
        globals()["app"] = build()
        return globals()["app"]
    raise AttributeError(name)
