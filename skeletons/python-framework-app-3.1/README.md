# ${{ values.name }}

${{ values.description }}

An application of the Refresquito platform in three layers, created from the Backstage template
"New application (Python Framework)" and built with the Python Framework:

| Layer | What | Built with |
|---|---|---|
| Web | `frontend/`: Angular 20. The list of ${{ values.entities }}, the form, sign in and out | [`refresquito-angular`](https://github.com/javivillar/refresquito-angular) |
| API | `backend/`: FastAPI. `/api/${{ values.entities }}`, documented on `/api/docs` | [`refresquito-fastapi`](https://github.com/javivillar/refresquito-fastapi) |
| Data | PostgreSQL 16, schema kept by Alembic migrations (`backend/migrations/`) | |

Users come from Keycloak. Two realm roles: `${{ values.name }}-viewer` reads, `${{ values.name }}-admin` also
creates, edits and deletes. The web only hides what a role cannot do; the API is what refuses it.

It starts as a working copy of the [petstore](https://github.com/javivillar/petstore), the reference
application of the framework, with one entity: `${{ values.entityTitle }}` (name, category, status and start
date). Change it into what the application is about; the tests tell you what you broke.

## Run it locally

```bash
podman compose up -d db                      # PostgreSQL on localhost:55432 (also docker compose)

cd backend
python3 -m venv .venv && .venv/bin/pip install --find-links ../vendor -e '.[dev]'
export RQ_DATABASE_URL=postgresql+asyncpg://${{ values.name }}:${{ values.name }}@localhost:55432/${{ values.name }}
export RQ_OIDC_ISSUER=https://iam.<domain>/realms/RefresquitoTime
export RQ_OIDC_CA_FILE=~/pki-<zone>-<program>/root_ca.crt    # only with a cluster CA
.venv/bin/alembic upgrade head
.venv/bin/uvicorn ${{ values.name }}.main:app --reload       # http://localhost:8000/api/docs

cd ../frontend
npm ci
npm start                                    # http://localhost:4200, /api proxied to :8000
```

`frontend/public/config.json` says which Keycloak the web uses in development. The realm needs
the public client `${{ values.name }}` allowing `http://localhost:4200/*`, and the two roles: they come
with the deployment on the platform (below).

## Tests

```bash
cd backend && .venv/bin/pytest               # against the PostgreSQL above; fails under 80 % coverage
cd frontend && npm test                      # headless; KARMA_BROWSER=FirefoxHeadless without Chrome
```

The backend tests use the schema the migrations create, and tokens signed by
`refresquito_fastapi.testing`, so they need no Keycloak. The frontend tests use
`refresquito-angular/testing` the same way.

Linters: `cd backend && .venv/bin/ruff check . && .venv/bin/mypy` and `cd frontend && npm run lint` (eslint).

### Quality report

Each run of the CI writes the quality report `quality.json` (`.github/quality.py`): tests and coverage of both parts,
ruff and mypy of the backend, eslint of the frontend. Its tables are in the summary of the jobs `backend` and
`frontend`; on `main` it is attached to both images next to their SBOM (artifact type
`application/vnd.refresquito.quality.v1+json`). The scorecard *Quality & Security* of Backstage reads it from the
image deployed. Coverage below its threshold and ruff fail the CI; mypy and eslint only report for now.
Besides the numbers it has the detail of each part: every test with its result and time, and every file with its
coverage and the lines no test runs (the frontend's tests come from the reporter `specs` of `karma.conf.js`). The
card *Tests & coverage* of that tab shows it.

### Code findings

The quality report also says what is wrong in the code itself. Nothing here fails the CI: the scorecard shows it and
its checks decide.

| Part | Tool | What |
|---|---|---|
| `backend.endpoints` | `.github/endpoints.py` | who can call each operation: `roles` (`require_roles`), `user` (`CurrentUser`), `flow` (`FlowCaller`), `custom` (a security scheme of its own), `public` (declared) or `none`. `unauthenticated` counts the operations with **no authentication that are not declared public** |
| `backend.bandit` | Bandit on `backend/src` | static analysis of the Python code, by severity |
| `frontend.security` | the block *Security* of `eslint.config.js` | `eval`, HTML written by hand, `bypassSecurityTrust*`, a token in `localStorage` |
| `secrets` | gitleaks on the whole git history (job `secrets`), Trivy on each image | keys, tokens or passwords committed or copied into an image |

An operation that is public on purpose says so, with the reason:

```python
@router.get("/api/info", openapi_extra={"x-refresquito-public": "version shown on the sign-in page"})
```

The detail gives the rule, the file and the line, never the secret. A secret found in the history has to be revoked
where it was issued: rewriting the history does not make it secret again. Locally:

```bash
cd backend && .venv/bin/python ../.github/endpoints.py ${{ values.name }}.main:build /tmp/endpoints.json && .venv/bin/bandit -r src
cd ../frontend && npx eslint src
```

## The contract between web and API

`backend/openapi.json` is the OpenAPI document of the API. The web generates its types from it
every time it is built, tested or served (`npm run gen:api`, not committed). After changing the API:

```bash
cd backend && .venv/bin/python -m ${{ values.name }}.openapi > openapi.json
```

The CI fails if that file is not what the API publishes.

## Images

The CI of `main` pushes `ghcr.io/${{ values.owner }}/${{ values.name }}-api` and `${{ values.name }}-web`, tagged with
the commit.

| Image | Listens on | Configuration |
|---|---|---|
| `${{ values.name }}-api` | 8000 | `RQ_DATABASE_URL`, `RQ_OIDC_ISSUER`, and the other `RQ_*` of refresquito-fastapi. It runs the migrations before serving |
| `${{ values.name }}-web` | 8080 | `KEYCLOAK_URL` (required), `KEYCLOAK_REALM`, `KEYCLOAK_CLIENT_ID`, `APP_API_URL` (empty: same origin). Written to `config.json` at start-up, so one image runs on any cluster |

## On the platform

The application is one file in [`refresquito-services`](https://github.com/javivillar/refresquito-services):
`bootstrap/app-of-apps/apps/${{ values.name }}.yaml`, proposed by the template in a pull request. It says where it
runs, the commit of each stage (dev, pre, pro) and the platform blocks it uses; merging it deploys it. The template
"Promote an application (Python Framework)" moves a commit on to the next stage.
{%- if values.processes or values.flows or values.dashboards or (values.buckets | length) or (values.sites | length) %}

## Platform blocks

The blocks marked when it was created come with example code, one file each (refresquito-fastapi 3.1 gives each
declared block as a dependency; refresquito-angular 3.1 the components):

| Block | API | Web |
|---|---|---|
{%- if values.processes %}
| `processes` (Camunda) | `review.py`: `POST /api/${{ values.entities }}/{id}/review` starts `platform/processes/${{ values.name }}-review.bpmn`; `GET /api/tasks`, `POST /api/tasks/{id}/complete` | *Ask for a review*, *My tasks* |
{%- endif %}
{%- if values.flows %}
| `flows` (Activepieces) | `welcome.py`: `POST /api/${{ values.entities }}/{id}/welcome`, the answer of `platform/flows/new-${{ values.entity }}.json`; the event `${{ values.entity }}.created` (`api.py`); the runs of its flows, `GET /api/flow-runs` (table `flow_run`) | *Welcome*, *Flows* |
{%- endif %}
{%- if values.dashboards %}
| `dashboards` (Superset) | `dashboards.py`: `GET /api/dashboards`, `GET /api/dashboards/{name}/guest-token` (the export of `platform/dashboards/`) and `GET /api/stats/${{ values.entities }}-by-status` (the rows of its dataset) | *Dashboard* (`<rq-dashboard>`) |
{%- endif %}
{%- if values.buckets | length %}
| `s3` (SeaweedFS) | `files.py`: `/api/${{ values.entities }}/{id}/files` in the bucket `${{ values.buckets[0] }}` (downloads with a presigned URL) | *Files* of a ${{ values.entity }} |
{%- endif %}
{%- if values.sites | length %}
| `dms` (Alfresco) | `documents.py`: `/api/${{ values.entities }}/{id}/documents` in the site `${{ values.sites[0] }}` | *Documents* of a ${{ values.entity }} |
{%- endif %}

Locally no block is declared: those endpoints answer 500 `platform_block_not_declared`. The tests use the fakes of
`refresquito_fastapi.testing`.
{%- endif %}

## Logs and the audit trail

The API writes two streams, both JSON on stdout, told apart by `log_type`: `application` (its logs and one line per
request) and `audit` (who did what). Every write (`POST`, `PUT`, `PATCH`, `DELETE`) and every refused request (401,
403) is audited by itself, with the user, the route, the outcome and the request ID. What matters to the business is
audited by the code:

```python
from refresquito_fastapi import audit

audit("${{ values.entity }}.archive", resource=f"${{ values.entity }}/{item.id}")
```

On the platform each stream is its own in Loki (`{namespace_name="<namespace>", log_type="audit"}`), and every event
counts in `audit_events_total{action, outcome}` on `/metrics`, scraped by Prometheus. Grafana has both in the
dashboard *Python Framework - Audit*. Never put secrets or personal data you do not need in an event.

## `vendor/`

The two parts of the framework, as the packages of their releases (the versions `backend/pyproject.toml` and `frontend/package.json` name): neither can be
installed from a build without a token yet. Once they can, replace `--find-links ../vendor` and
the `file:` dependency of `frontend/package.json` with the published packages, and delete it.
