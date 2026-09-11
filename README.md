# backstage-templates

Backstage [`Template`](https://backstage.io/docs/features/software-templates/)
entity catalog for self-service resource management across the Refresquito
stack: Keycloak identities (`RefresquitoTime` realm), Superset connections/
datasets/charts/dashboards, and Camunda (`bpm-oneke`) process definitions.
Consumed by
[`javivillar/backstage-app`](https://github.com/javivillar/backstage-app) —
see that repo's `plugins/keycloak-backend`, `plugins/superset-backend` and
`plugins/camunda-backend` for the scaffolder actions these templates call,
and [`FORK.md`](https://github.com/javivillar/backstage-app/blob/main/FORK.md)
for how the whole self-service feature set fits together.

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

26 templates across 4 self-service resource families, each keeping every
mutation owner-scoped (per-creator ownership — see each backend plugin's own
README in `backstage-app` for the exact mechanism used per family):

### Keycloak identities (`keycloak-backend`) — create/update/delete trio per object kind

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

Ownership is a bolted-on `backstage_owner` attribute (Keycloak has no native
ownership concept) — every `create-*`/`update-*`/`delete-*` action is
reachable by any signed-in user with the `backstage` client's `access` role,
not admin-gated; ownership is what stops user A from editing user B's
objects, not who can run the template.

### Superset resources (`superset-backend`) — create/update for connections & datasets, provision-only for charts/dashboards

| Template (`metadata.name`) | Title | Action called |
| --- | --- | --- |
| `superset-create-connection` | Create Superset Connection | `superset:create-connection` |
| `superset-update-connection` | Update Superset Connection | `superset:update-connection` |
| `superset-create-dataset` | Create Superset Dataset | `superset:create-dataset` |
| `superset-update-dataset` | Update Superset Dataset | `superset:update-dataset` |
| `superset-provision-chart` | Provision Superset Chart | `superset:provision-chart` |
| `superset-provision-dashboard` | Provision Superset Dashboard | `superset:provision-dashboard` |

Charts/dashboards are provision-only (deep-links into Superset's own visual
editor for the rest) — see `plugins/superset-backend`'s README for why.
Ownership: native `owners` relation for chart/dataset/dashboard, a
bolted-on `extra.backstage_owner` for connections (Superset's `Database`
object has no native ownership relation at all).

### Camunda process definitions (`camunda-backend`) — full create/update/delete trio

| Template (`metadata.name`) | Title | Action called |
| --- | --- | --- |
| `camunda-provision-process` | Provision Camunda Process | `camunda:provision-process` |
| `camunda-update-process` | Update Camunda Process | `camunda:update-process` |
| `camunda-delete-process` | Delete Camunda Process | `camunda:delete-process` |

Every provisioned process is pre-wired with per-instance isolation (the
same `executionListener`/`assignee` pattern documented in
`refresquito-services`' `AUTHZ.md` § bpm-oneke §6) and a
definition-level ownership grant made directly in Camunda's own native
authorization table — see `plugins/camunda-backend`'s README for why this
one doesn't need a bolted-on attribute the way Keycloak/Superset do.

### SeaweedFS object storage resources (`seaweedfs-backend`) — full create/delete for buckets, table buckets, groups & policies

| Template (`metadata.name`) | Title | Action called |
| --- | --- | --- |
| `seaweedfs-create-bucket` | Create SeaweedFS Bucket | `seaweedfs:create-bucket` |
| `seaweedfs-delete-bucket` | Delete SeaweedFS Bucket | `seaweedfs:delete-bucket` |
| `seaweedfs-create-table-bucket` | Create SeaweedFS Table Bucket | `seaweedfs:create-table-bucket` |
| `seaweedfs-delete-table-bucket` | Delete SeaweedFS Table Bucket | `seaweedfs:delete-table-bucket` |
| `seaweedfs-create-group` | Create SeaweedFS Group | `seaweedfs:create-group` |
| `seaweedfs-delete-group` | Delete SeaweedFS Group | `seaweedfs:delete-group` |
| `seaweedfs-create-policy` | Create SeaweedFS Policy | `seaweedfs:create-policy` |
| `seaweedfs-delete-policy` | Delete SeaweedFS Policy | `seaweedfs:delete-policy` |

Ownership: native `owner` field for buckets/table buckets (SeaweedFS
persists it); a bolted-on ownership table in Backstage's own database for
groups/policies (SeaweedFS's `Group`/`Policy` objects have no owner/extra
field at all to hook into) — see `plugins/seaweedfs-backend`'s README for
the full split. Creating a bucket also auto-grants the creator a
bucket-scoped IAM policy so it's actually usable afterward via SeaweedFS's
own File Browser, not just visible in Backstage. Attaching a policy to a
group (done from the `/seaweedfs-manager` page, not a template — see below)
only ever offers policies the caller themself created.

All 26 are `owner: group:default/backstage-admin` (the *template* owner —
who can edit the template definition — unrelated to per-object ownership,
which is what actually gates edit/delete of the objects these templates
create).

The `/keycloak-manager`, `/superset-manager`, `/camunda-manager` and
`/seaweedfs-manager` pages in `backstage-app` navigate here with
`?formData=...` pre-filled for Edit/Delete rather than duplicating any of
this logic — this catalog is the only place the actual input schemas live.
Group-policy attach/detach is the one exception: it's an interactive
manager-page feature, not a template, since editing an existing group's
policy list needs a live, ownership-scoped picker a one-shot form can't
easily do — see `plugins/seaweedfs`'s README.

## Adding a new template

1. Add a `---`-separated `Template` document to `catalog-info.yaml`
   (`apiVersion: scaffolder.backstage.io/v1beta3`).
2. If it calls a new action (not one of the 26 above), the action itself has
   to be added to the relevant `*-backend` plugin in `backstage-app` first
   and deployed — a template whose `action:` doesn't exist on the backend
   fails at run time, not at import time, so there's no early warning if
   this order is skipped.
3. Push to `main`. No build/CI here — Backstage picks it up on its next
   catalog refresh poll.
