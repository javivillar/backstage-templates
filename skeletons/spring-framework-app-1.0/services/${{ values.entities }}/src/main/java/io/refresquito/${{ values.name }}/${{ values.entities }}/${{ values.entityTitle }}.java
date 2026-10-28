package io.refresquito.${{ values.name }}.${{ values.entities }};

import java.time.LocalDate;
import java.time.OffsetDateTime;

import jakarta.persistence.Column;
import jakarta.persistence.Entity;
import jakarta.persistence.EnumType;
import jakarta.persistence.Enumerated;
import jakarta.persistence.GeneratedValue;
import jakarta.persistence.GenerationType;
import jakarta.persistence.Id;
import jakarta.persistence.Table;

/** A ${{ values.entity }} (V1__${{ values.entity }}.sql). */
@Entity
@Table(name = "${{ values.entity }}")
public class ${{ values.entityTitle }} {

    public enum Status { active, pending, closed }

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    Long id;
    String name;
    String category;
    @Enumerated(EnumType.STRING)
    Status status = Status.active;
    LocalDate startDate;
    @Column(updatable = false)
    OffsetDateTime createdAt;
    String createdBy;

    public Long getId() { return id; }
    public String getName() { return name; }
    public String getCategory() { return category; }
    public Status getStatus() { return status; }
    public LocalDate getStartDate() { return startDate; }
    public OffsetDateTime getCreatedAt() { return createdAt; }
    public String getCreatedBy() { return createdBy; }
}
