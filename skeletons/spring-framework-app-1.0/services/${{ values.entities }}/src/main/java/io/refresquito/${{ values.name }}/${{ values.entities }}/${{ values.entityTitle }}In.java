package io.refresquito.${{ values.name }}.${{ values.entities }};

import java.time.LocalDate;

import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.PastOrPresent;
import jakarta.validation.constraints.Size;
import org.jspecify.annotations.Nullable;

/** What the API receives: the same fields and rules as the ${{ values.name }}. */
public record ${{ values.entityTitle }}In(
        @NotBlank @Size(max = 80) String name,
        @NotBlank @Size(max = 40) String category,
        ${{ values.entityTitle }}.@Nullable Status status,
        @PastOrPresent(message = "it cannot be in the future") @Nullable LocalDate startDate) {
}
