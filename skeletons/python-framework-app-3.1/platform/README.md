# platform/ — what this application brings to the platform

Content the platform deploys for this application, versioned with its code: the Dockerfile of the API copies this
folder into its image (`/app/platform`), and the stack takes it from the image of the commit that is deployed. So what
runs in the platform is always the version of the application that runs.

| Folder | What | Used when |
|---|---|---|
| `processes/` | BPMN processes, DMN decisions and forms for Camunda 7 | the block `processes` of the application is on |
| `dashboards/` | Dashboards for Superset: a dashboard exported from Superset (Dashboards, ⋮, Export), unzipped here as it comes | the block `dashboards` of the application is on |
| `flows/` | Flows for Activepieces: each one a flow exported from Activepieces (the flow's menu, Export), saved as `<flow>.json` | the block `flows` of the application is on |
| `monitoring/` | Grafana dashboards of its own (optional), one JSON per file, besides the standard Logs and Performance | the block `monitoring` of the application is on |

**Naming rule:** the `id` of every executable process and decision starts with the name of the application followed by
a dash (`${{ values.name }}-review`). An application never deploys over another one's; a file with another id is refused.

**Dashboards:** whatever connection the export has, the stack imports it over the database of the application in each
cluster, read with a read-only role. Make them in Superset on any database with the same tables, export, unzip here.

**Flows:** one flow per file; the name of the file (lower case, digits and dashes) names its webhook. The stack imports
a flow when its file changes and publishes it once complete; a flow that uses connections waits until someone creates
them in the project of the application in Activepieces (connections hold credentials: never here). The API finds the
webhook of each flow that starts with one in `ACTIVEPIECES_FLOW_<FLOW>_URL` (`<FLOW>`: the name of the file in
capitals, dashes as `_`; add `/sync` to wait for its answer).

**Monitoring:** with the block `monitoring` (on by default), Prometheus scrapes the metrics of the API and Grafana
gets, in the folder `apps`, the dashboards `<title> - Logs` and `<title> - Performance` of each stage, made by the
platform: nothing to write here. A dashboard of its own is a Grafana JSON (a dashboard's JSON model) saved in
`monitoring/<name>.json`; `$namespace` in its queries is the namespace of the deployment, and the data sources are the
variables `prometheus` and `loki`. A file `logs.json` or `performance.json` replaces the standard one. Grafana gets it
again when the file changes.

The application talks to Camunda as itself (`CAMUNDA_URL`, `CAMUNDA_USERNAME`, `CAMUNDA_PASSWORD` in the environment
of the API). How it works: `charts/python-app-oneke/INSTALL.md` of
[`refresquito-services`](https://github.com/javivillar/refresquito-services/blob/main/charts/python-app-oneke/INSTALL.md),
"Block `processes`".
