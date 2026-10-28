package io.refresquito.${{ values.name }}.${{ values.entities }};

import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;

/** ${{ values.entities }}: the primary service of the ${{ values.title }}. */
@SpringBootApplication
public class ${{ values.entitiesTitle }}Application {

    /** The roles of the ${{ values.title }} (block sso of its file in refresquito-services). */
    public static final String VIEWER = "${{ values.name }}-viewer";
    public static final String ADMIN = "${{ values.name }}-admin";

    public static void main(String[] args) {
        SpringApplication.run(${{ values.entitiesTitle }}Application.class, args);
    }
}
