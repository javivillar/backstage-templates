# The image of one service of the ${{ values.title }}. Build from the root of the repository:
#   podman build -f services/Dockerfile --build-arg SERVICE=${{ values.entities }} -t ${{ values.name }}-${{ values.entities }} .
# The base images are build args: Docker Hardened Images in CI (dhi.io, or the cache of Harbor in the cluster), the
# upstream ones below anywhere else.
ARG BUILD_IMAGE=docker.io/library/maven:3.9-eclipse-temurin-25
ARG RUNTIME_IMAGE=docker.io/library/eclipse-temurin:25-jre-alpine

FROM ${BUILD_IMAGE} AS build
ARG SERVICE
# DHI build images run as nonroot (uid 65532): build in a folder that user owns.
WORKDIR /tmp/src
# the poms and the framework first: the dependencies stay in a layer of their own while only the code changes
COPY --chown=65532:65532 pom.xml ./
COPY --chown=65532:65532 vendor/maven vendor/maven
COPY --chown=65532:65532 services/${{ values.entities }}/pom.xml services/${{ values.entities }}/
COPY --chown=65532:65532 services/notifier/pom.xml services/notifier/
RUN test -n "${SERVICE}" || (echo "--build-arg SERVICE=<service> is required" && exit 1); \
    mvn -q -B -pl services/${SERVICE} dependency:go-offline
COPY --chown=65532:65532 services/${SERVICE}/src services/${SERVICE}/src
RUN mvn -q -B -o -pl services/${SERVICE} package -DskipTests \
 && java -Djarmode=tools -jar services/${SERVICE}/target/*.jar extract --layers --launcher --destination /tmp/out

FROM ${RUNTIME_IMAGE}
WORKDIR /app
# Spring Boot layers: least to most often changed, for layer caching.
COPY --from=build /tmp/out/dependencies/ ./
COPY --from=build /tmp/out/spring-boot-loader/ ./
COPY --from=build /tmp/out/snapshot-dependencies/ ./
COPY --from=build /tmp/out/application/ ./
USER 65532
# the chart sets JAVA_TOOL_OPTIONS from serviceDefaults.jvmOptions; this is the default outside it
ENV JAVA_TOOL_OPTIONS="-XX:MaxRAMPercentage=75 -XX:+ExitOnOutOfMemoryError"
EXPOSE 8080
ENTRYPOINT ["java", "org.springframework.boot.loader.launch.JarLauncher"]
