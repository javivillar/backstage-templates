# refresquito-postgres — the database of the Python Framework (line 3.2): the official PostgreSQL image, made smaller
# in what it carries and run without root.
#   - gosu goes: the official image only uses it to drop root at start-up, and it is built with an old Go whose
#     standard library brought almost every vulnerability of the image. This image starts as postgres.
#   - wget goes too (busybox): the database does not download anything, and it is where the one known vulnerability
#     of busybox is (CVE-2025-60876, no fix yet).
#   - the packages of Alpine are brought up to date when the image is built.
# Everything else is the official image: the same entrypoint, POSTGRES_USER / POSTGRES_PASSWORD / POSTGRES_DB, the
# scripts of /docker-entrypoint-initdb.d and the data in /var/lib/postgresql (PostgreSQL 18: PGDATA is
# /var/lib/postgresql/18/docker). The base is pinned: a new PostgreSQL or Alpine is a new release of this image.
FROM docker.io/library/postgres:18.6-alpine3.24

ARG VERSION=3.2.0
LABEL org.opencontainers.image.title="refresquito-postgres" \
      org.opencontainers.image.description="PostgreSQL of the Python Framework of the Refresquito platform: no root, no gosu" \
      org.opencontainers.image.version="${VERSION}" \
      org.opencontainers.image.source="https://github.com/javivillar/refresquito-postgres" \
      org.opencontainers.image.licenses="LicenseRef-Refresquito-Proprietary AND PostgreSQL"

RUN apk upgrade --no-cache \
 && rm -f /usr/local/bin/gosu /usr/bin/wget /bin/wget \
 && mkdir -p /var/run/postgresql /var/lib/postgresql \
 && chown -R postgres:postgres /var/run/postgresql /var/lib/postgresql

# uid and gid 70, as in the official alpine image: a volume must be writable by them (fsGroup 70 in Kubernetes)
USER 70:70
