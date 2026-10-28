# Release notes of ${{ values.name }}

One entry per version, newest first. The version is the same in `pom.xml` (the root and each service) and
`frontend/package.json`.

## 0.1.0

Created from the Backstage template "New application (Spring Framework)": the ${{ values.entities }}.

- Service `${{ values.entities }}` (`/api/${{ values.entities }}`): list with filters and pages, read, create, update and
  delete, on its own PostgreSQL with Flyway migrations; it publishes `${{ values.entity }}.created` and
  `${{ values.entity }}.status-changed`.
- Service `notifier`: no API; it handles the events of the application (`@OnEvent`) and keeps a notice of each, once.
- Web: the list, the form, sign in and out with Keycloak.
- Roles: `${{ values.name }}-viewer` reads, `${{ values.name }}-admin` also writes.
- Data catalog: `platform/datahub.yaml` (what it declares for DataHub) and `platform/datahub-exceptions.yaml`
  (classification exceptions, approved by the data stewards: `.github/CODEOWNERS`).
- Built with refresquito-spring-boot 1.0.0-SNAPSHOT, refresquito-angular 3.3.1 and refresquito-postgres 3.3.0.
- License: Apache-2.0 (`LICENSE`), like the Spring Framework.
- Security exceptions: `platform/security-exceptions.yaml` (empty), approved by the security approvers
  (`.github/CODEOWNERS`), validated by the CI into the quality report; Backstage applies the active ones to its checks.
- CI: the quality report `quality.json` (tests, coverage, who can call each operation, secrets in the git history and
  in the images), an image per part with its SBOM.
{%- if values.processes %}
- Block `processes`: `POST /api/${{ values.entities }}/{id}/review` starts its process `review`; *My tasks* (`/api/tasks`).
{%- endif %}
{%- if values.flows %}
- Block `flows`: `POST /api/${{ values.entities }}/{id}/welcome` waits for the flow `new-${{ values.entity }}`; the event
  `${{ values.entity }}.created` starts it too; `POST /api/${{ values.entities }}/{id}/status` for its flows only.
{%- endif %}
{%- if values.dashboards %}
- Block `dashboards`: its Superset dashboard embedded (page *Dashboard*, `GET /api/dashboards`) and the data of its
  dataset `${{ values.entity }}` (`GET /api/stats/${{ values.entities }}-by-status`).
{%- endif %}
{%- if values.buckets | length %}
- Block `s3`: the files of each ${{ values.entity }} in the bucket `${{ values.buckets[0] }}`.
{%- endif %}
{%- if values.sites | length %}
- Block `dms`: the documents of each ${{ values.entity }} in the Alfresco site `${{ values.sites[0] }}`.
{%- endif %}
