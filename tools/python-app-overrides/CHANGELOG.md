# Release notes of ${{ values.name }}

One entry per version, newest first. The version is the same in `backend/pyproject.toml`,
`backend/src/${{ values.name }}/__init__.py` and `frontend/package.json`.

## 0.1.0

Created from the Backstage template "New application (Python Framework)": the ${{ values.entities }}.

- API (`/api/${{ values.entities }}`): list with filters and pages, read, create, update and delete, on PostgreSQL with migrations.
- Web: the list, the form, sign in and out with Keycloak.
- Roles: `${{ values.name }}-viewer` reads, `${{ values.name }}-admin` also writes.
- Built with refresquito-fastapi 0.1.0 and refresquito-angular 0.1.0.
