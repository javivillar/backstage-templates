package io.refresquito.${{ values.name }}.${{ values.entities }};

import java.util.Optional;

import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.JpaSpecificationExecutor;

public interface ${{ values.entitiesTitle }} extends JpaRepository<${{ values.entityTitle }}, Long>, JpaSpecificationExecutor<${{ values.entityTitle }}> {
    Optional<${{ values.entityTitle }}> findByName(String name);
}
