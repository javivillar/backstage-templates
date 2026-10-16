# Release notes of ${{ values.name }}

One entry per version, newest first. The version is the same in `backend/pyproject.toml`,
`backend/src/${{ values.name }}/__init__.py` and `frontend/package.json`.

## 0.1.0

Created from the Backstage template "New application (Python Framework)": the ${{ values.entities }}.

- API (`/api/${{ values.entities }}`): list with filters and pages, read, create, update and delete, on PostgreSQL with migrations.
- Web: the list, the form, sign in and out with Keycloak.
- Roles: `${{ values.name }}-viewer` reads, `${{ values.name }}-admin` also writes.
- Built with refresquito-fastapi 3.0.1 and refresquito-angular 3.0.0.
{%- if values.processes %}
- Block `processes`: `POST /api/${{ values.entities }}/{id}/review` starts its process `review`; *My tasks* (`/api/tasks`).
{%- endif %}
{%- if values.flows %}
- Block `flows`: `POST /api/${{ values.entities }}/{id}/welcome` waits for the flow `new-${{ values.entity }}`.
{%- endif %}
{%- if values.buckets | length %}
- Block `s3`: the files of each ${{ values.entity }} in the bucket `${{ values.buckets[0] }}`.
{%- endif %}
{%- if values.sites | length %}
- Block `dms`: the documents of each ${{ values.entity }} in the Alfresco site `${{ values.sites[0] }}`.
{%- endif %}
