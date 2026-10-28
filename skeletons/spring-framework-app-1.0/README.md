# ${{ values.name }}

${{ values.description }}

An application of the Refresquito platform made of services, created from the Backstage template
"New application (Spring Framework)" and built with the Spring Framework:

| Part | What | Built with |
|---|---|---|
| Web | `frontend/`: Angular 20. The list of ${{ values.entities }}, the form, sign in and out | [`refresquito-angular`](https://github.com/javivillar/refresquito-angular) |
| Service `${{ values.entities }}` | `services/${{ values.entities }}`: `/api/${{ values.entities }}`, its OpenAPI at `/api/openapi.json` | [`refresquito-spring-boot`](https://github.com/javivillar/refresquito-spring-boot) |
| Service `notifier` | `services/notifier`: no API. It handles the events of the others and keeps a notice of each | idem |
| Data | One PostgreSQL 18 per service (refresquito-postgres, the database of the framework: `vendor/`), schema kept by Flyway (`src/main/resources/db/migration`) | |

Users come from Keycloak. Two realm roles: `${{ values.name }}-viewer` reads, `${{ values.name }}-admin` also
creates, edits and deletes. The web only hides what a role cannot do; the services refuse it.

It starts as a working copy of [petstore-spring](https://github.com/javivillar/petstore-spring), the reference
application of the framework, with one entity: `${{ values.entityTitle }}` (name, category, status and start date).
Change it into what the application is about, and add services as it grows; the tests tell you what you broke.

## How the services work together

```
web ──/api/${{ values.entities }}──▶ ${{ values.entities }} ──${{ values.entity }}.created, ${{ values.entity }}.status-changed──▶ RabbitMQ ──▶ notifier
```

- **Events:** a service publishes in the same transaction as its data (`Events.publish`, an outbox in its database:
  the event exists if and only if the change does) and any service handles them with `@OnEvent`, once. RabbitMQ is
  the block `events` of the platform: a virtual host of the application, created when it is deployed.
- **REST between services:** a new service that needs another one declares it (`calls: [${{ values.entities }}]` in the
  file of the application on the platform) and calls it with `ServiceClients.forService("${{ values.entities }}")`,
  passing the token of the user on. [petstore-spring](https://github.com/javivillar/petstore-spring) has an example:
  its service `adoptions` calls `pets`.
- **A new service:** copy `services/notifier` (the smallest) to `services/<name>`, rename its package, add it to the
  `<modules>` of `pom.xml`, to `services/Dockerfile`, to `dev/initdb/10-services.sql` if it has a database, and to the
  `services` of the file of the application on the platform. The CI builds an image `${{ values.name }}-<name>` for
  every folder of `services/`.

Each service with an API publishes its OpenAPI at `/api/openapi.json`; the committed copy
(`services/<service>/openapi.json`) is what the web generates its types from (`npm run gen:api`, every time it is
built, tested or served; not committed) and what the catalog of Backstage shows. A test of each service checks it is
up to date: `RQ_UPDATE_OPENAPI=1 mvn test` writes it again after a change of the API.

## Run it locally

Java 25 and Maven 3.9+, Node 20, podman (or docker).

```bash
mvn test                                     # every service, against real PostgreSQL (Testcontainers); fails if openapi.json is stale

podman compose up -d                         # PostgreSQL (a database per service) and RabbitMQ
DB_HOST=localhost DB_PORT=55432 DB_DATABASE=${{ values.entities }} DB_USERNAME=${{ values.entities }} DB_PASSWORD=${{ values.entities }} \
RABBITMQ_HOST=localhost RABBITMQ_PORT=55672 RABBITMQ_USERNAME=${{ values.name }} RABBITMQ_PASSWORD=${{ values.name }} \
RQ_OIDC_ISSUER=https://iam.<domain>/realms/RefresquitoTime RQ_OIDC_CLIENT_ID=${{ values.name }} \
mvn -pl services/${{ values.entities }} spring-boot:run      # http://localhost:8080/api/openapi.json

cd frontend && npm ci && npm start           # http://localhost:4200
```

`frontend/public/config.json` says which Keycloak and which API the web uses in development. The realm needs the
public client `${{ values.name }}` allowing `http://localhost:4200/*`, and the two roles: they come with the
deployment on the platform (below).

## Tests

```bash
mvn test                                     # Testcontainers (podman: DOCKER_HOST=unix:///run/user/$UID/podman/podman.sock)
cd frontend && npm test                      # headless; KARMA_BROWSER=FirefoxHeadless without Chrome
```

The services' tests use tokens signed by `refresquito-spring-boot-test` (`TokenFactory`), so they need no Keycloak;
the blocks of the platform are stand-ins (one test class per block). The frontend tests use
`refresquito-angular/testing` the same way. Coverage: JaCoCo (`target/site/jacoco/`) and karma.

### Quality report

Each run of the CI writes the quality report `quality.json` (`.github/quality.py`): the tests and coverage of the
services (Surefire, JaCoCo) and of the web (karma), eslint, and who can call each operation. On `main` it is attached
to every image next to its SBOM (artifact type `application/vnd.refresquito.quality.v1+json`); the scorecard
*Quality & Security* of Backstage reads it from the images deployed, with every test and the lines no test runs.

### Code findings

| Part | Tool | What |
|---|---|---|
| `backend.endpoints` | `x-refresquito-auth` of the OpenAPI of each service (written by the framework as it enforces it) | who can call each operation: `roles` (`@RolesAllowed`), `user` (any signed-in user), `flow` (its flows only), `public` (`@PermitAll` or `refresquito.security.public-paths`). Every route needs a user of the realm unless declared public |
| `frontend.security` | the block *Security* of `eslint.config.js` | `eval`, HTML written by hand, `bypassSecurityTrust*`, a token in `localStorage` |
| `secrets` | gitleaks on the whole git history (job `secrets`), Trivy on each image | keys, tokens or passwords committed or copied into an image |

A finding that is accepted goes in `platform/security-exceptions.yaml` (the format is in its comments): check, id,
why, who approved it and until when, at most 12 months. Only the security approvers can approve it: they are its
CODEOWNERS (`.github/CODEOWNERS`).

## Images

The CI of `main` pushes, tagged with the commit, to `ghcr.io/${{ values.owner }}`:

| Image | What | Configuration |
|---|---|---|
| `${{ values.name }}-<service>` | each service (`services/Dockerfile`, `--build-arg SERVICE=<service>`), port 8080 | what the platform gives (`RQ_*`, `DB_*`, `RABBITMQ_*`, the blocks): refresquito-spring-boot reads it by itself |
| `${{ values.name }}-web` | the web (nginx), port 8080 | `KEYCLOAK_URL` (required), `KEYCLOAK_REALM`, `KEYCLOAK_CLIENT_ID`, `APP_API_URL` (empty: same origin), written to `config.json` at start-up |
| `${{ values.name }}-platform` | `platform/` for the provisioner of the platform (the service images have no shell) | |

The services are built on Docker Hardened Images when the repository has the secrets `DHI_USERNAME` / `DHI_TOKEN`
(a Docker Hub token), on the upstream images otherwise.

## On the platform

The application is one file in [`refresquito-services`](https://github.com/javivillar/refresquito-services):
`bootstrap/app-of-apps/apps/${{ values.name }}.yaml`, proposed by the template in a pull request. It says where it
runs, the commit of each stage (dev, pre, pro), its services and the platform blocks it uses; merging it deploys it
with the chart `spring-app-oneke`: a Deployment and a PostgreSQL per service, the web, the routes of the host, and
Grafana's dashboards Logs, Audit and Performance per service.
{%- if values.processes or values.flows or values.dashboards or (values.buckets | length) or (values.sites | length) %}

## Platform blocks

The blocks marked when it was created come with example code in the service `${{ values.entities }}`, one controller
and one test class each:

| Block | Service | Web |
|---|---|---|
{%- if values.processes %}
| `processes` (Camunda) | `ReviewController`: `POST /api/${{ values.entities }}/{id}/review` starts `platform/processes/${{ values.name }}-review.bpmn`; `GET /api/tasks`, `POST /api/tasks/{id}/complete` | *Ask for a review*, *My tasks* |
{%- endif %}
{%- if values.flows %}
| `flows` (Activepieces) | `WelcomeController`: `POST /api/${{ values.entities }}/{id}/welcome`, the answer of `platform/flows/new-${{ values.entity }}.json`; the event `${{ values.entity }}.created` starts it too; the runs of its flows, `GET /api/flow-runs` | *Welcome*, *Flows* |
{%- endif %}
{%- if values.dashboards %}
| `dashboards` (Superset) | `DashboardsController`: `GET /api/dashboards`, `GET /api/dashboards/{name}/guest-token` (the export of `platform/dashboards/`) and `GET /api/stats/${{ values.entities }}-by-status` (the rows of its dataset) | *Dashboard* (`<rq-dashboard>`) |
{%- endif %}
{%- if values.buckets | length %}
| `s3` (SeaweedFS) | `FilesController`: `/api/${{ values.entities }}/{id}/files` in the bucket `${{ values.buckets[0] }}` (downloads with a presigned URL) | *Files* of a ${{ values.entity }} |
{%- endif %}
{%- if values.sites | length %}
| `dms` (Alfresco) | `DocumentsController`: `/api/${{ values.entities }}/{id}/documents` in the site `${{ values.sites[0] }}` | *Documents* of a ${{ values.entity }} |
{%- endif %}

Locally no block is declared: those routes answer 503 `<block>_not_configured`.
{%- endif %}

## `vendor/`

The framework this version is built with: `vendor/maven` (refresquito-spring-boot: its parent, starter and test kit,
as a Maven repository the poms read, `file:vendor/maven`), the package of refresquito-angular, and the Dockerfile of
refresquito-postgres, which `compose.yaml` and the CI build. Moving to a new version of the framework is copying it
here again (`scripts/vendor.sh <this folder>` of refresquito-spring-boot) and running the tests.

## License

Apache-2.0 (`LICENSE`).
