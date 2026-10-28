# ${{ values.title }} frontend. Build from the root of the repository:  podman build -f frontend/Dockerfile .
FROM docker.io/library/node:20-alpine AS build
WORKDIR /src
COPY vendor/refresquito-angular-3.3.1.tgz ./vendor/
COPY frontend/package.json frontend/package-lock.json ./frontend/
RUN cd frontend && npm ci
COPY frontend ./frontend
# the API types are generated from it (npm run gen:api, which 'npm run build' runs first)
COPY services/${{ values.entities }}/openapi.json ./services/${{ values.entities }}/openapi.json
RUN cd frontend && npm run build && rm dist/frontend/browser/config.json

FROM docker.io/nginxinc/nginx-unprivileged:1.27-alpine
COPY frontend/deploy/nginx.conf /etc/nginx/conf.d/default.conf
COPY frontend/deploy/40-config-json.sh /docker-entrypoint.d/40-config-json.sh
COPY --from=build /src/frontend/dist/frontend/browser /usr/share/nginx/html
EXPOSE 8080
