package io.refresquito.${{ values.name }}.${{ values.entities }};

import java.net.http.HttpRequest;
import java.net.http.HttpResponse;
import java.nio.charset.StandardCharsets;

import io.refresquito.spring.dashboards.Dashboards;
import io.refresquito.spring.dms.Documents;
import io.refresquito.spring.flows.Flows;
import io.refresquito.spring.processes.Processes;
import io.refresquito.spring.s3.Storage;
import org.junit.jupiter.api.BeforeEach;
import org.springframework.test.context.bean.override.mockito.MockitoBean;

/**
 * The tests of the platform blocks (S3, Alfresco, Camunda, Activepieces, Superset), each block a stand-in: the
 * framework talks to the real ones (its own tests); here, that each route asks the right block for the right thing.
 * One test class per block, so an application keeps the tests of the blocks it uses.
 */
abstract class BlockTest extends ServiceTest {

    @MockitoBean Storage storage;
    @MockitoBean Documents documents;
    @MockitoBean Processes processes;
    @MockitoBean Flows flows;
    @MockitoBean Dashboards dashboards;
    long rex;

    @BeforeEach
    void rex() {
        rex = saved("Rex", "tools", ${{ values.entityTitle }}.Status.active);
    }

    /** A form with one file, as <rq-file-upload> sends it. */
    HttpResponse<String> upload(String path, String name, String content, String... roles) throws Exception {
        String boundary = "rq-boundary";
        String form = "--" + boundary + "\r\nContent-Disposition: form-data; name=\"file\"; filename=\"" + name + "\"\r\n"
                + "Content-Type: text/plain\r\n\r\n" + content + "\r\n--" + boundary + "--\r\n";
        return send("POST", path, HttpRequest.BodyPublishers.ofString(form, StandardCharsets.UTF_8),
                "multipart/form-data; boundary=" + boundary, roles);
    }
}
