#!/usr/bin/env python3
"""Who can call each endpoint of the API: the part `endpoints` of the quality report (quality.json).

    python3 ../.github/endpoints.py <app>.main:build endpoints.json     (in backend/, with the app installed)

It builds the application the way `python -m <app>.openapi` does (no database, no Keycloak) and looks at the
dependencies of every operation, the way FastAPI resolves them:

    roles    it depends on require_roles(...) of refresquito-fastapi: a user with one of those roles
    user     it depends on current_user (CurrentUser): any signed-in user of the realm, for this service
    flow     it depends on FlowCaller (block flows): only the flows of the application, with its key (X-Flow-Key)
    custom   it has a security scheme that is not the framework's (a bearer / API key of its own): checked by hand
    public   no authentication, DECLARED: openapi_extra={"x-refresquito-public": "<why>"} on the operation
    none     no authentication and not declared public: a FINDING of the quality report

The operations of the framework itself (/health, /metrics, the OpenAPI and its docs) are listed with owner
"framework" and never count as findings: the framework decides who can call them.
"""
import argparse
import importlib
import json
import sys

PUBLIC = "x-refresquito-public"


def calls(dependant, seen=None):
    """Every callable of the dependency tree of an operation (FastAPI's Dependant)."""
    seen = seen if seen is not None else set()
    for dep in dependant.dependencies:
        if id(dep) in seen:
            continue
        seen.add(id(dep))
        yield dep
        yield from calls(dep, seen)


def roles_of(func):
    """The roles of a check made by refresquito_fastapi.require_roles(*roles) (they live in its closure)."""
    if not getattr(func, "__qualname__", "").startswith("require_roles.<locals>"):
        return None
    for cell in func.__closure__ or ():
        value = cell.cell_contents
        if isinstance(value, tuple) and all(isinstance(r, str) for r in value):
            return list(value)
    return []


RANK = {"none": 0, "custom": 1, "flow": 2, "user": 3, "roles": 4}


def describe(route, known):
    """known: {dependency of the framework: kind of authentication}"""
    auth, roles, schemes = "none", [], False
    for dep in calls(route.dependant):
        found = roles_of(dep.call)
        kind = "roles" if found is not None else known.get(dep.call)
        if found:
            roles = sorted(set(roles) | set(found))
        if kind and RANK[kind] > RANK[auth]:
            auth = kind
        if getattr(dep, "security_scopes", None) is not None or type(dep.call).__module__.startswith("fastapi.security"):
            schemes = True
    reason = (route.openapi_extra or {}).get(PUBLIC)
    if auth == "none" and schemes:
        auth = "custom"
    if auth == "none" and reason:
        auth = "public"
    module = getattr(route.endpoint, "__module__", "") or ""
    owner = "framework" if module.split(".")[0] in ("refresquito_fastapi", "fastapi", "starlette") else "app"
    entry = {"method": ",".join(sorted(route.methods - {"HEAD", "OPTIONS"})), "path": route.path, "auth": auth,
             "owner": owner, "operation": route.name}
    if roles:
        entry["roles"] = roles
    if reason:
        entry["reason"] = str(reason)
    return entry


def effective_routes(app, api_route):
    """The operations as the application serves them: with the prefix and the dependencies of the routers that
    include them. FastAPI >= 0.160 keeps included routers as they are and resolves them on use (iter_route_contexts,
    what its own OpenAPI generation walks); before, app.routes already held the copies."""
    from fastapi import routing
    if hasattr(routing, "iter_route_contexts"):
        yield from routing.iter_route_contexts(app.routes)
    else:
        yield from app.routes


def build_app(target):
    module_name, _, attr = target.partition(":")
    obj = getattr(importlib.import_module(module_name), attr or "app")
    if callable(obj) and not hasattr(obj, "routes"):
        from refresquito_fastapi import Settings
        obj = obj(Settings(app_name=module_name.split(".")[0], log_level="ERROR"))
    return obj


def main():
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    p.add_argument("app", help="module:factory or module:app, e.g. ${{ values.name }}.main:build")
    p.add_argument("out")
    a = p.parse_args()
    from fastapi.routing import APIRoute
    from refresquito_fastapi.auth import current_user
    known = {current_user: "user"}
    try:                                              # block flows (the extra of the framework may be missing)
        from refresquito_fastapi.platform.flows import flow_caller
        known[flow_caller] = "flow"
    except ImportError:
        pass

    app = build_app(a.app)
    endpoints = []
    for route in effective_routes(app, APIRoute):
        if isinstance(getattr(route, "original_route", route), APIRoute):
            endpoints.append(describe(route, known))
        elif getattr(route, "path", None):            # the OpenAPI document and its docs pages (Starlette routes)
            endpoints.append({"method": ",".join(sorted((getattr(route, "methods", None) or {"GET"}) - {"HEAD"})),
                              "path": route.path, "auth": "none", "owner": "framework", "operation": route.name})
    endpoints.sort(key=lambda e: (e["owner"] != "app", e["path"], e["method"]))
    mine = [e for e in endpoints if e["owner"] == "app"]
    report = {
        "total": len(mine),
        "unauthenticated": sum(e["auth"] == "none" for e in mine),
        "public": sum(e["auth"] == "public" for e in mine),
        "custom": sum(e["auth"] == "custom" for e in mine),
        "with_roles": sum(e["auth"] == "roles" for e in mine),
        "flow": sum(e["auth"] == "flow" for e in mine),
        "endpoints": endpoints,
    }
    with open(a.out, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2)
    for e in mine:
        if e["auth"] == "none":
            print(f"::warning::{e['method']} {e['path']} ({e['operation']}) has no authentication: depend on "
                  f"CurrentUser / require_roles, or declare it public with openapi_extra={{'{PUBLIC}': '<why>'}}")
    print(json.dumps({k: v for k, v in report.items() if k != "endpoints"}))
    return 0


if __name__ == "__main__":
    sys.exit(main())
