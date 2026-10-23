# Release notes of ${{ values.name }}

One entry per version, newest first. The version is the same in `backend/pyproject.toml`,
`backend/src/${{ values.name }}/__init__.py` and `frontend/package.json`.

## 0.1.0

Created from the Backstage template "New application (Python Framework)": the ${{ values.entities }}.

- API (`/api/${{ values.entities }}`): list with filters and pages, read, create, update and delete, on PostgreSQL with migrations.
- Web: the list, the form, sign in and out with Keycloak.
- Roles: `${{ values.name }}-viewer` reads, `${{ values.name }}-admin` also writes.
- Data catalog: `platform/datahub.yaml` (what it declares for DataHub) and `platform/datahub-exceptions.yaml`
  (classification exceptions, approved by the data stewards: `.github/CODEOWNERS`).
- Built with refresquito-fastapi 3.1.1 and refresquito-angular 3.1.1.
- Its database: refresquito-postgres (PostgreSQL 18, no root), built from `vendor/` by `compose.yaml` and the CI.
- License: proprietary (`LicenseRef-Refresquito-Proprietary`, `backend/LICENSE` and `frontend/package.json`), like the
  frameworks: the license policy of Backstage checks that every dependency of its images says its license.
- Security exceptions: `platform/security-exceptions.yaml` (empty), approved by the security approvers
  (`.github/CODEOWNERS`), validated by the CI into the quality report; Backstage applies the active ones to its checks.
- CI: the quality report `quality.json` with its code findings (README, *Code findings*): who can call each endpoint,
  Bandit, the eslint rules of security, secrets in the git history and in the images.
{%- if values.processes %}
- Block `processes`: `POST /api/${{ values.entities }}/{id}/review` starts its process `review`; *My tasks* (`/api/tasks`).
{%- endif %}
{%- if values.flows %}
- Block `flows`: `POST /api/${{ values.entities }}/{id}/welcome` waits for the flow `new-${{ values.entity }}`; creating a
  ${{ values.entity }} publishes the event `${{ values.entity }}.created`, which starts it too; the runs of its flows
  (`GET /api/flow-runs`, page *Flows*) and `POST /api/${{ values.entities }}/{id}/status` for its flows only.
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
