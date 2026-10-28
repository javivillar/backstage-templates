package io.refresquito.${{ values.name }}.${{ values.entities }};

import java.time.LocalDate;
import java.time.OffsetDateTime;
import org.jspecify.annotations.Nullable;

/** What the API answers: {id, name, category, status, start_date, created_at, created_by}, as the ${{ values.name }}. */
public record ${{ values.entityTitle }}Out(Long id, String name, String category, ${{ values.entityTitle }}.Status status, @Nullable LocalDate startDate,
                     OffsetDateTime createdAt, String createdBy) {

    static ${{ values.entityTitle }}Out of(${{ values.entityTitle }} ${{ values.entity }}) {
        return new ${{ values.entityTitle }}Out(${{ values.entity }}.id, ${{ values.entity }}.name, ${{ values.entity }}.category, ${{ values.entity }}.status, ${{ values.entity }}.startDate, ${{ values.entity }}.createdAt, ${{ values.entity }}.createdBy);
    }
}
