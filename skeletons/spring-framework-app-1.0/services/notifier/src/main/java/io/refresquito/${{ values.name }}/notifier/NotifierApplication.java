package io.refresquito.${{ values.name }}.notifier;

import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;

/** notifier: listens to the events of the ${{ values.title }} and keeps its notices. */
@SpringBootApplication
public class NotifierApplication {
    public static void main(String[] args) {
        SpringApplication.run(NotifierApplication.class, args);
    }
}
