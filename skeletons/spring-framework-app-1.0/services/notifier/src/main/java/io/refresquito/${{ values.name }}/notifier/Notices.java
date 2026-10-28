package io.refresquito.${{ values.name }}.notifier;

import java.util.Map;

import io.refresquito.spring.audit.Audit;
import io.refresquito.spring.events.EventMetadata;
import io.refresquito.spring.events.OnEvent;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.jdbc.core.JdbcTemplate;
import org.springframework.stereotype.Component;

/**
 * The notices of the ${{ values.title }}, from its events: a new ${{ values.entity }} and a change of status, for everyone. In
 * the transaction of the framework that records the event as handled, so each one is written once; its
 * audit line carries the request that caused it (request_id, user) and its trace goes on from it.
 */
@Component
public class Notices {

    private static final Logger LOG = LoggerFactory.getLogger(Notices.class);
    private final JdbcTemplate jdbc;
    private final Audit audit;

    Notices(JdbcTemplate jdbc, Audit audit) {
        this.jdbc = jdbc;
        this.audit = audit;
    }

    @OnEvent("${{ values.entity }}.created")
    void ${{ values.entity }}Created(Map<String, Object> ${{ values.entity }}, EventMetadata metadata) {
        notice(metadata, null, "New in the shop: " + ${{ values.entity }}.get("name") + " (" + ${{ values.entity }}.get("category") + ")");
    }

    @OnEvent("${{ values.entity }}.status-changed")
    void ${{ values.entity }}StatusChanged(Map<String, Object> ${{ values.entity }}, EventMetadata metadata) {
        notice(metadata, null, ${{ values.entity }}.get("name") + " is now " + ${{ values.entity }}.get("status"));
    }

    private void notice(EventMetadata metadata, String recipient, String text) {
        jdbc.update("insert into notice (event_id, type, recipient, text) values (?, ?, ?, ?) on conflict (event_id) do nothing",
                metadata.id(), metadata.type(), recipient, text);
        audit.record("notice.send", "notice/" + metadata.type(), Audit.Outcome.SUCCESS,
                recipient == null ? Map.of("event", metadata.id()) : Map.of("event", metadata.id(), "recipient", recipient));
        LOG.atInfo().addKeyValue("type", metadata.type()).addKeyValue("recipient", recipient).log("notice");
    }
}
