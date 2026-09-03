# backstage-templates

Backstage [`Template`](https://backstage.io/docs/features/software-templates/)
entity catalog for Keycloak self-service identity management on the
`RefresquitoTime` realm. Consumed by
[`javivillar/backstage-app`](https://github.com/javivillar/backstage-app) —
see that repo's [`plugins/keycloak-backend`](https://github.com/javivillar/backstage-app/tree/main/plugins/keycloak-backend)
for the `keycloak:*` scaffolder actions these templates call, and
[`FORK.md`](https://github.com/javivillar/backstage-app/blob/main/FORK.md)
for how the whole Keycloak self-service feature fits together.

## How this repo is wired in

Backstage does **not** get this repo's URL from anything in
`backstage-app` itself — `app-config.yaml`/`app-config.production.yaml`
there are unmodified upstream defaults. The real `catalog.locations` entry
is rendered at deploy time by the GitOps chart, from
`javivillar/refresquito-services`:

- `charts/cnoe-oneke/values.yaml` → `backstage.catalogLocation` (currently
  `.../javivillar/backstage-templates/blob/main/catalog-info.yaml`)
- `charts/cnoe-oneke/templates/backstage-config.yaml` → renders that value
  into the `catalog.locations` the Backstage pod actually reads.

Backstage polls this URL and re-imports on change — there's no webhook/CI
here, just `git push` to `main`.

## Why one `catalog-info.yaml` and not a template per file

Backstage supports both `Location` entities that point at many files and a
single file with multiple YAML documents. This repo deliberately uses **one
file, all templates inlined** (commit `f1b627a2`, after an earlier attempt
at separate files/refs didn't import cleanly) — if you add a template,
append a new `---`-separated document to `catalog-info.yaml` rather than
creating a new file; a new file will not be picked up without also adding a
`Location` entry for it.

## Templates

All 9 exist to keep every Keycloak mutation self-service with per-creator
ownership (see `plugins/keycloak-backend`'s README in `backstage-app` for
the ownership model) — one create/update/delete trio per object kind:

| Template (`metadata.name`) | Title | Action called |
| --- | --- | --- |
| `keycloak-create-user` | Create Keycloak User | `keycloak:create-user` |
| `keycloak-update-user` | Update Keycloak User | `keycloak:update-user` |
| `keycloak-delete-user` | Delete Keycloak User | `keycloak:delete-user` |
| `keycloak-create-group` | Create Keycloak Group | `keycloak:create-group` |
| `keycloak-update-group` | Rename Keycloak Group | `keycloak:update-group` |
| `keycloak-delete-group` | Delete Keycloak Group | `keycloak:delete-group` |
| `keycloak-create-client` | Create Keycloak OIDC Client | `keycloak:create-client` |
| `keycloak-update-client` | Update Keycloak OIDC Client | `keycloak:update-client` |
| `keycloak-delete-client` | Delete Keycloak OIDC Client | `keycloak:delete-client` |

All 9 are `owner: group:default/backstage-admin` (the *template* owner —
who can edit the template definition — which is unrelated to
`backstage_owner`, the per-object attribute the actions themselves stamp on
whatever Keycloak object gets created, see `plugins/keycloak-backend`).
Every `create-*`/`update-*`/`delete-*` action is reachable by any
signed-in user with the `backstage` client's `access` role — not
admin-gated — ownership is what stops user A from editing user B's objects,
not who can run the template.

The `/keycloak-manager` page in `backstage-app` (`plugins/keycloak`)
navigates here with `?formData=...` pre-filled for Edit/Delete rather than
duplicating any of this logic — this catalog is the only place the actual
input schemas live.

## Adding a new template

1. Add a `---`-separated `Template` document to `catalog-info.yaml`
   (`apiVersion: scaffolder.backstage.io/v1beta3`).
2. If it calls a new action (not one of the 9 `keycloak:*` ones above), the
   action itself has to be added to `plugins/keycloak-backend` in
   `backstage-app` first and deployed — a template whose `action:` doesn't
   exist on the backend fails at run time, not at import time, so there's
   no early warning if this order is skipped.
3. Push to `main`. No build/CI here — Backstage picks it up on its next
   catalog refresh poll.
