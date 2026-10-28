package io.refresquito.${{ values.name }}.notifier;

import java.nio.charset.StandardCharsets;
import java.time.Duration;
import java.util.UUID;

import io.refresquito.spring.test.TokenFactory;
import org.junit.jupiter.api.AfterAll;
import org.junit.jupiter.api.Test;
import org.springframework.amqp.core.Message;
import org.springframework.amqp.core.MessageProperties;
import org.springframework.amqp.rabbit.connection.CachingConnectionFactory;
import org.springframework.amqp.rabbit.core.RabbitTemplate;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.jdbc.core.JdbcTemplate;
import org.springframework.test.context.DynamicPropertyRegistry;
import org.springframework.test.context.DynamicPropertySource;
import org.testcontainers.containers.PostgreSQLContainer;
import org.testcontainers.containers.RabbitMQContainer;
import org.testcontainers.junit.jupiter.Testcontainers;
import org.testcontainers.utility.DockerImageName;

import static org.assertj.core.api.Assertions.assertThat;

/**
 * notifier against a real RabbitMQ 4.4 and PostgreSQL 18: the events that ${{ values.entities }} publishes (the exchange
 * refresquito.events of the virtual host of the ${{ values.title }}) become notices, each one once.
 */
@Testcontainers(disabledWithoutDocker = true)
@SpringBootTest(properties = "refresquito.events.retry-delay=100ms")
class NoticesTest {

    static final PostgreSQLContainer<?> DB = new PostgreSQLContainer<>(DockerImageName.parse(
            System.getProperty("postgres.image", "docker.io/library/postgres:18-alpine")).asCompatibleSubstituteFor("postgres"))
            .withDatabaseName("notifier").withUsername("notifier").withPassword("notifier");
    static final RabbitMQContainer RABBIT = new RabbitMQContainer(DockerImageName.parse(
            System.getProperty("rabbitmq.image", "docker.io/library/rabbitmq:4.4.0-management-alpine")).asCompatibleSubstituteFor("rabbitmq"));
    static final TokenFactory TOKENS = TokenFactory.start("${{ values.name }}");

    static {
        DB.start();
        RABBIT.start();
    }

    @DynamicPropertySource
    static void platform(DynamicPropertyRegistry registry) {
        TOKENS.register(registry);
        registry.add("spring.datasource.url", DB::getJdbcUrl);
        registry.add("spring.datasource.username", DB::getUsername);
        registry.add("spring.datasource.password", DB::getPassword);
        registry.add("spring.rabbitmq.host", RABBIT::getHost);
        registry.add("spring.rabbitmq.port", RABBIT::getAmqpPort);
        registry.add("spring.rabbitmq.username", RABBIT::getAdminUsername);
        registry.add("spring.rabbitmq.password", RABBIT::getAdminPassword);
    }

    @AfterAll
    static void stop() {
        TOKENS.close();
    }

    @Autowired
    JdbcTemplate jdbc;

    void publish(String type, String json, UUID id) {
        CachingConnectionFactory cf = new CachingConnectionFactory(RABBIT.getHost(), RABBIT.getAmqpPort());
        cf.setUsername(RABBIT.getAdminUsername());
        cf.setPassword(RABBIT.getAdminPassword());
        try {
            MessageProperties p = new MessageProperties();
            p.setMessageId(id.toString());
            p.setType(type);
            p.setAppId("${{ values.entities }}");
            p.setContentType("application/json");
            p.setHeader("x-refresquito-user", "eva");
            new RabbitTemplate(cf).send("refresquito.events", type, new Message(json.getBytes(StandardCharsets.UTF_8), p));
        } finally {
            cf.destroy();
        }
    }

    int notices(String type) throws InterruptedException {
        long until = System.nanoTime() + Duration.ofSeconds(15).toNanos();
        int found = 0;
        while (System.nanoTime() < until) {
            found = jdbc.queryForObject("select count(*) from notice where type = ?", Integer.class, type);
            if (found > 0) break;
            Thread.sleep(200);
        }
        Thread.sleep(500);   // a repeated delivery would be in by now
        return jdbc.queryForObject("select count(*) from notice where type = ?", Integer.class, type);
    }

    @Test
    void a_change_of_status_is_a_notice_for_everyone_once() throws Exception {
        UUID id = UUID.randomUUID();
        String event = "{\"id\":7,\"name\":\"Rex\",\"status\":\"closed\"}";
        publish("${{ values.entity }}.status-changed", event, id);
        publish("${{ values.entity }}.status-changed", event, id);    // RabbitMQ delivers at least once: the same event again
        assertThat(notices("${{ values.entity }}.status-changed")).isEqualTo(1);
        assertThat(jdbc.queryForObject("select text from notice where type = '${{ values.entity }}.status-changed'", String.class))
                .isEqualTo("Rex is now closed");
    }

    @Test
    void a_new_${{ values.entity }}_is_a_notice_for_everyone() throws Exception {
        publish("${{ values.entity }}.created", "{\"id\":8,\"name\":\"Kiwi\",\"category\":\"bird\"}", UUID.randomUUID());
        assertThat(notices("${{ values.entity }}.created")).isEqualTo(1);
        assertThat(jdbc.queryForObject("select text from notice where type = '${{ values.entity }}.created'", String.class))
                .isEqualTo("New in the shop: Kiwi (bird)");
    }
}
