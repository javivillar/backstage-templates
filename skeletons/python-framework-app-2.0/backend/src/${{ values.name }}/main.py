"""The application: uvicorn ${{ values.name }}.main:app"""

from refresquito_fastapi import Settings, create_app

from . import __version__
from .api import router


def build(settings: Settings | None = None, **options: object):
    settings = settings or Settings(app_name="${{ values.name }}")
    return create_app(
        settings,
        title="${{ values.title }} API",
        version=__version__,
        routers=[router],
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
