package io.refresquito.${{ values.name }}.${{ values.entities }};

import io.refresquito.spring.error.RefresquitoException;
import org.springframework.beans.factory.ObjectProvider;

/** A platform block the service uses: there when the platform gives its variables, else a 503 that says which. */
final class Blocks {

    private Blocks() {
    }

    static <T> T required(ObjectProvider<T> block, String name) {
        T found = block.getIfAvailable();
        if (found == null) {
            throw new RefresquitoException.ServiceUnavailable(name + "_not_configured",
                    "The block " + name + " of the platform is not declared for this deployment");
        }
        return found;
    }

    /** The name of an uploaded file without its folders (a browser may send a path), or the fallback. */
    static String basename(String name, String fallback) {
        if (name == null || name.isBlank()) return fallback;
        String clean = name.replace('\\', '/');
        return clean.substring(clean.lastIndexOf('/') + 1);
    }
}
