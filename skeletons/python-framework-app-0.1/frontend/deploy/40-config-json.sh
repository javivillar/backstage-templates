#!/bin/sh
# config.json of this deployment, from the environment. The same image runs on any cluster.
set -eu
: "${KEYCLOAK_URL:?set KEYCLOAK_URL, e.g. https://iam.<domain>}"
cat > /tmp/config.json <<JSON
{
  "apiUrl": "${APP_API_URL:-}",
  "keycloak": {
    "url": "${KEYCLOAK_URL}",
    "realm": "${KEYCLOAK_REALM:-RefresquitoTime}",
    "clientId": "${KEYCLOAK_CLIENT_ID:-${{ values.name }}}"
  },
  "logLevel": "${APP_LOG_LEVEL:-info}"
}
JSON
echo "config.json: API '${APP_API_URL:-<same origin>}', Keycloak ${KEYCLOAK_URL} realm ${KEYCLOAK_REALM:-RefresquitoTime}"
