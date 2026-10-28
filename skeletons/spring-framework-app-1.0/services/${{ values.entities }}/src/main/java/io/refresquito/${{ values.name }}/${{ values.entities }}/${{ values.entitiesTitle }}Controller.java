package io.refresquito.${{ values.name }}.${{ values.entities }};

import java.time.OffsetDateTime;
import java.util.Map;

import io.refresquito.spring.error.RefresquitoException;
import io.refresquito.spring.events.Events;
import io.refresquito.spring.flows.Flows;
import io.refresquito.spring.openapi.Lineage;
import io.refresquito.spring.security.RefresquitoUser;
import io.refresquito.spring.web.Page;
import jakarta.annotation.security.RolesAllowed;
import jakarta.validation.Valid;
import org.springframework.beans.factory.ObjectProvider;
import org.springframework.data.domain.PageRequest;
import org.springframework.data.domain.Sort;
import org.springframework.data.jpa.domain.Specification;
import org.springframework.http.HttpStatus;
import org.springframework.transaction.annotation.Transactional;
import org.springframework.web.bind.annotation.DeleteMapping;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.PutMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.ResponseStatus;
import org.springframework.web.bind.annotation.RestController;

import static io.refresquito.${{ values.name }}.${{ values.entities }}.${{ values.entitiesTitle }}Application.ADMIN;
import static io.refresquito.${{ values.name }}.${{ values.entities }}.${{ values.entitiesTitle }}Application.VIEWER;

/** The ${{ values.entities }}. Reading needs a role of the ${{ values.title }}; writing, the admin one. */
@RestController
@RequestMapping("/api/${{ values.entities }}")
public class ${{ values.entitiesTitle }}Controller {

    private final ${{ values.entitiesTitle }} ${{ values.entities }};
    private final ObjectProvider<Events> events;
    private final ObjectProvider<Flows> flows;

    ${{ values.entitiesTitle }}Controller(${{ values.entitiesTitle }} ${{ values.entities }}, ObjectProvider<Events> events, ObjectProvider<Flows> flows) {
        this.${{ values.entities }} = ${{ values.entities }};
        this.events = events;
        this.flows = flows;
    }

    ${{ values.entityTitle }} find(long id) {
        return ${{ values.entities }}.findById(id).orElseThrow(() -> new RefresquitoException.NotFound("${{ values.entityTitle }} " + id + " does not exist"));
    }

    private void checkNameIsFree(String name, Long except) {
        ${{ values.entities }}.findByName(name).filter(other -> !other.id.equals(except)).ifPresent(other -> {
            throw new RefresquitoException(409, "${{ values.entity }}_name_taken", "There is already a ${{ values.entity }} called " + name);
        });
    }

    @GetMapping
    @RolesAllowed({VIEWER, ADMIN})
    @Lineage(source = "table:${{ values.entity }}")
    public Page<${{ values.entityTitle }}Out> list(@RequestParam(defaultValue = "1") int page, @RequestParam(defaultValue = "20") int size,
                             @RequestParam(required = false) ${{ values.entityTitle }}.Status status, @RequestParam(required = false) String category) {
        if (page < 1 || size < 1 || size > 100) {
            throw new RefresquitoException(422, "validation_error", "page is 1 or more, size from 1 to 100");
        }
        Specification<${{ values.entityTitle }}> where = (root, query, cb) -> cb.conjunction();
        if (status != null) where = where.and((root, query, cb) -> cb.equal(root.get("status"), status));
        if (category != null && !category.isBlank()) where = where.and((root, query, cb) -> cb.equal(root.get("category"), category.strip()));
        var found = ${{ values.entities }}.findAll(where, PageRequest.of(page - 1, size, Sort.by("name")));
        return new Page<>(found.map(${{ values.entityTitle }}Out::of).getContent(), found.getTotalElements(), page, size);
    }

    @GetMapping("/{id}")
    @RolesAllowed({VIEWER, ADMIN})
    @Lineage(source = "table:${{ values.entity }}")
    public ${{ values.entityTitle }}Out one(@PathVariable long id) {
        return ${{ values.entityTitle }}Out.of(find(id));
    }

    @PostMapping
    @ResponseStatus(HttpStatus.CREATED)
    @RolesAllowed(ADMIN)
    @Transactional
    @Lineage(target = "table:${{ values.entity }}")
    public ${{ values.entityTitle }}Out create(@Valid @RequestBody ${{ values.entityTitle }}In body, RefresquitoUser user) {
        checkNameIsFree(body.name().strip(), null);
        ${{ values.entityTitle }} ${{ values.entity }} = new ${{ values.entityTitle }}();
        apply(${{ values.entity }}, body);
        ${{ values.entity }}.createdAt = OffsetDateTime.now();
        ${{ values.entity }}.createdBy = user.username();
        ${{ values.entities }}.saveAndFlush(${{ values.entity }});
        Map<String, Object> event = Map.of("id", ${{ values.entity }}.id, "name", ${{ values.entity }}.name, "category", ${{ values.entity }}.category);
        // to the other services of the ${{ values.title }} (block events: in the transaction of the ${{ values.entity }}), and to its flows
        events.ifAvailable(e -> e.publish("${{ values.entity }}.created", event));
        flows.ifAvailable(f -> f.publish("${{ values.entity }}.created", event));
        return ${{ values.entityTitle }}Out.of(${{ values.entity }});
    }

    @PutMapping("/{id}")
    @RolesAllowed(ADMIN)
    @Transactional
    @Lineage(target = "table:${{ values.entity }}")
    public ${{ values.entityTitle }}Out update(@PathVariable long id, @Valid @RequestBody ${{ values.entityTitle }}In body) {
        ${{ values.entityTitle }} ${{ values.entity }} = find(id);
        checkNameIsFree(body.name().strip(), id);
        ${{ values.entityTitle }}.Status before = ${{ values.entity }}.status;
        apply(${{ values.entity }}, body);
        if (before != ${{ values.entity }}.status) {
            events.ifAvailable(e -> e.publish("${{ values.entity }}.status-changed", Map.of("id", ${{ values.entity }}.id, "name", ${{ values.entity }}.name, "status", ${{ values.entity }}.status.name())));
        }
        return ${{ values.entityTitle }}Out.of(${{ values.entity }});
    }

    @DeleteMapping("/{id}")
    @ResponseStatus(HttpStatus.NO_CONTENT)
    @RolesAllowed(ADMIN)
    @Transactional
    @Lineage(target = "table:${{ values.entity }}")
    public void delete(@PathVariable long id) {
        ${{ values.entities }}.delete(find(id));
    }

    private static void apply(${{ values.entityTitle }} ${{ values.entity }}, ${{ values.entityTitle }}In body) {
        ${{ values.entity }}.name = body.name().strip();
        ${{ values.entity }}.category = body.category().strip();
        ${{ values.entity }}.status = body.status() != null ? body.status() : ${{ values.entityTitle }}.Status.active;
        ${{ values.entity }}.startDate = body.startDate();
    }
}
