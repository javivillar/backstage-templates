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

The stack deploys it with a chart of its own, `charts/${{ values.name }}-oneke` of
[`refresquito-services`](https://github.com/javivillar/refresquito-services). That chart, its
Keycloak client and roles in the realm file and its place in the catalog are generated in that
repository by one command, with the commit whose images to deploy:

```bash
python3 bootstrap/add-python-app.py ${{ values.name }} --title "${{ values.title }}" \
  --entity ${{ values.entity }} --entities ${{ values.entities }} --tag <commit of main>
```

Open a pull request with the result; once merged, a bootstrap pass with `${{ values.name }}-oneke` in
`RQ_APPS` installs it. To roll out a later commit, set it as `image.tag` of the chart.

## `vendor/`

The two parts of the framework, as the packages their `v0.1.0` tags produce: neither can be
installed from a build without a token yet. Once they can, replace `--find-links ../vendor` and
the `file:` dependency of `frontend/package.json` with the published packages, and delete it.
