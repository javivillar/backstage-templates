# platform/ — what this application brings to the platform

Content the platform deploys for this application, versioned with its code: the Dockerfile of the API copies this
folder into its image (`/app/platform`), and the stack takes it from the image of the commit that is deployed. So what
runs in the platform is always the version of the application that runs.

| Folder | What | Used when |
|---|---|---|
| `processes/` | BPMN processes, DMN decisions and forms for Camunda 7 | the block `processes` of the application is on |

**Naming rule:** the `id` of every executable process and decision starts with the name of the application followed by
a dash (`${{ values.name }}-review`). An application never deploys over another one's; a file with another id is refused.

The application talks to Camunda as itself (`CAMUNDA_URL`, `CAMUNDA_USERNAME`, `CAMUNDA_PASSWORD` in the environment
of the API). How it works: `charts/python-app-oneke/INSTALL.md` of
[`refresquito-services`](https://github.com/javivillar/refresquito-services/blob/main/charts/python-app-oneke/INSTALL.md),
"Block `processes`".
