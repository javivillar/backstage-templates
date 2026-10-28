package io.refresquito.${{ values.name }}.${{ values.entities }};

import java.net.URI;
import java.net.http.HttpClient;
import java.net.http.HttpRequest;
import java.net.http.HttpResponse;
import java.time.OffsetDateTime;

import io.refresquito.spring.test.TokenFactory;
import org.junit.jupiter.api.BeforeEach;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.boot.test.web.server.LocalServerPort;
import org.springframework.test.context.DynamicPropertyRegistry;
import org.springframework.test.context.DynamicPropertySource;
import org.testcontainers.containers.PostgreSQLContainer;
import org.testcontainers.junit.jupiter.Testcontainers;
import org.testcontainers.utility.DockerImageName;
import tools.jackson.databind.json.JsonMapper;

/**
 * What every test of the service shares: a real PostgreSQL 18 (one for all the test classes), tokens of a realm made
 * in the test, and calls to the service as a user with some roles. No broker: the handlers of events are called
 * directly by the tests that need them.
 */
@Testcontainers(disabledWithoutDocker = true)
@SpringBootTest(webEnvironment = SpringBootTest.WebEnvironment.RANDOM_PORT, properties = {
        "refresquito.events.enabled=false", "management.health.rabbit.enabled=false"})
abstract class ServiceTest {

    static final PostgreSQLContainer<?> DB = new PostgreSQLContainer<>(DockerImageName.parse(
            System.getProperty("postgres.image", "docker.io/library/postgres:18-alpine")).asCompatibleSubstituteFor("postgres"))
            .withDatabaseName("${{ values.entities }}").withUsername("${{ values.entities }}").withPassword("${{ values.entities }}");
    static final TokenFactory TOKENS = TokenFactory.start("${{ values.name }}");
    static final HttpClient HTTP = HttpClient.newHttpClient();
    static final JsonMapper JSON = JsonMapper.builder().build();

    static {
        DB.start();
    }

    @DynamicPropertySource
    static void platform(DynamicPropertyRegistry registry) {
        TOKENS.register(registry);
        registry.add("spring.datasource.url", DB::getJdbcUrl);
        registry.add("spring.datasource.username", DB::getUsername);
        registry.add("spring.datasource.password", DB::getPassword);
    }

    @LocalServerPort
    int port;
    @Autowired
    ${{ values.entitiesTitle }} ${{ values.entities }};

    @BeforeEach
    void empty() {
        ${{ values.entities }}.deleteAll();
    }

    HttpResponse<String> send(String method, String path, HttpRequest.BodyPublisher body, String contentType, String... roles) throws Exception {
        HttpRequest.Builder b = HttpRequest.newBuilder(URI.create("http://127.0.0.1:" + port + path));
        if (roles.length > 0) b.header("Authorization", TOKENS.bearer("ana", roles));
        if (contentType != null) b.header("Content-Type", contentType);
        return HTTP.send(b.method(method, body).build(), HttpResponse.BodyHandlers.ofString());
    }

    HttpResponse<String> call(String method, String path, String json, String... roles) throws Exception {
        return send(method, path, json == null ? HttpRequest.BodyPublishers.noBody() : HttpRequest.BodyPublishers.ofString(json),
                json == null ? null : "application/json", roles);
    }

    /** A ${{ values.entity }} in the database, as an admin would have created it. */
    long saved(String name, String category, ${{ values.entityTitle }}.Status status) {
        ${{ values.entityTitle }} ${{ values.entity }} = new ${{ values.entityTitle }}();
        ${{ values.entity }}.name = name;
        ${{ values.entity }}.category = category;
        ${{ values.entity }}.status = status;
        ${{ values.entity }}.createdBy = "ana";
        ${{ values.entity }}.createdAt = OffsetDateTime.now();
        return ${{ values.entities }}.saveAndFlush(${{ values.entity }}).id;
    }
}
