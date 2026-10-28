package io.refresquito.${{ values.name }}.${{ values.entities }};

import java.net.URI;
import java.net.http.HttpRequest;
import java.net.http.HttpResponse;

import org.junit.jupiter.api.Test;
import tools.jackson.databind.JsonNode;

import static org.assertj.core.api.Assertions.assertThat;

/** The API of the ${{ values.entities }}: its data, its roles, its errors and its OpenAPI. */
class ${{ values.entitiesTitle }}Test extends ServiceTest {

    long create(String name, String category, String status) throws Exception {
        HttpResponse<String> created = call("POST", "/api/${{ values.entities }}",
                "{\"name\":\"" + name + "\",\"category\":\"" + category + "\",\"status\":\"" + status + "\"}", "${{ values.name }}-admin");
        assertThat(created.statusCode()).as(created.body()).isEqualTo(201);
        return JSON.readTree(created.body()).get("id").asLong();
    }

    @Test
    void an_admin_creates_reads_updates_and_deletes_a_${{ values.entity }}_with_the_json_of_the_${{ values.name }}() throws Exception {
        HttpResponse<String> created = call("POST", "/api/${{ values.entities }}",
                "{\"name\":\" Rex \",\"category\":\"dog\",\"start_date\":\"2024-05-01\"}", "${{ values.name }}-admin");
        assertThat(created.statusCode()).as(created.body()).isEqualTo(201);
        JsonNode ${{ values.entity }} = JSON.readTree(created.body());
        assertThat(${{ values.entity }}.get("name").asString()).isEqualTo("Rex");
        assertThat(${{ values.entity }}.get("status").asString()).isEqualTo("active");
        assertThat(${{ values.entity }}.get("start_date").asString()).isEqualTo("2024-05-01");
        assertThat(${{ values.entity }}.get("created_by").asString()).isEqualTo("ana");
        assertThat(${{ values.entity }}.has("created_at")).isTrue();
        long id = ${{ values.entity }}.get("id").asLong();

        assertThat(call("GET", "/api/${{ values.entities }}/" + id, null, "${{ values.name }}-viewer").body()).contains("\"name\":\"Rex\"");
        HttpResponse<String> updated = call("PUT", "/api/${{ values.entities }}/" + id, "{\"name\":\"Rex\",\"category\":\"dog\",\"status\":\"closed\"}", "${{ values.name }}-admin");
        assertThat(updated.statusCode()).isEqualTo(200);
        assertThat(updated.body()).contains("\"status\":\"closed\"");
        assertThat(call("DELETE", "/api/${{ values.entities }}/" + id, null, "${{ values.name }}-admin").statusCode()).isEqualTo(204);
        assertThat(call("GET", "/api/${{ values.entities }}/" + id, null, "${{ values.name }}-viewer").statusCode()).isEqualTo(404);
    }

    @Test
    void the_list_is_a_page_filtered_by_status_and_category() throws Exception {
        create("Ada", "books", "active");
        create("Kiwi", "bird", "closed");
        create("Rex", "tools", "active");
        JsonNode all = JSON.readTree(call("GET", "/api/${{ values.entities }}?size=2", null, "${{ values.name }}-viewer").body());
        assertThat(all.get("total").asLong()).isEqualTo(3);
        assertThat(all.get("page").asInt()).isEqualTo(1);
        assertThat(all.get("size").asInt()).isEqualTo(2);
        assertThat(all.get("items").findValuesAsString("name")).containsExactly("Ada", "Kiwi");
        JsonNode active = JSON.readTree(call("GET", "/api/${{ values.entities }}?status=active&category=tools", null, "${{ values.name }}-viewer").body());
        assertThat(active.get("items").findValuesAsString("name")).containsExactly("Rex");
    }

    @Test
    void the_roles_decide_who_reads_and_who_writes() throws Exception {
        assertThat(call("GET", "/api/${{ values.entities }}", null).statusCode()).isEqualTo(401);
        assertThat(call("GET", "/api/${{ values.entities }}", null, "someone-else").statusCode()).isEqualTo(403);
        HttpResponse<String> viewer = call("POST", "/api/${{ values.entities }}", "{\"name\":\"X\",\"category\":\"cat\"}", "${{ values.name }}-viewer");
        assertThat(viewer.statusCode()).isEqualTo(403);
        assertThat(viewer.body()).contains("\"code\":\"forbidden\"");
    }

    @Test
    void invalid_data_is_422_with_its_fields_and_a_taken_name_409() throws Exception {
        HttpResponse<String> invalid = call("POST", "/api/${{ values.entities }}", "{\"name\":\"\",\"category\":\"cat\",\"start_date\":\"2999-01-01\"}", "${{ values.name }}-admin");
        assertThat(invalid.statusCode()).isEqualTo(422);
        assertThat(invalid.body()).contains("\"code\":\"validation_error\"", "\"name\"", "\"start_date\"", "it cannot be in the future");
        create("Rex", "tools", "active");
        HttpResponse<String> taken = call("POST", "/api/${{ values.entities }}", "{\"name\":\"Rex\",\"category\":\"cat\"}", "${{ values.name }}-admin");
        assertThat(taken.statusCode()).isEqualTo(409);
        assertThat(taken.body()).contains("\"code\":\"${{ values.entity }}_name_taken\"");
    }

    @Test
    void a_block_the_deployment_does_not_declare_is_503_saying_which() throws Exception {
        long id = create("Rex", "tools", "active");
        assertThat(call("GET", "/api/${{ values.entities }}/" + id, null, "${{ values.name }}-viewer").statusCode()).isEqualTo(200);
{%- if (values.buckets | length) > 0 %}
        // block s3
        assertThat(call("GET", "/api/${{ values.entities }}/" + id + "/files", null, "${{ values.name }}-viewer").body()).contains("\"code\":\"s3_not_configured\"");
{%- endif %}
{%- if values.processes %}
        // block processes
        assertThat(call("GET", "/api/tasks", null, "${{ values.name }}-viewer").body()).contains("\"code\":\"processes_not_configured\"");
{%- endif %}
    }

    @Test
    void its_openapi_is_public_and_says_its_lineage() throws Exception {
        HttpResponse<String> openapi = call("GET", "/api/openapi.json", null);
        assertThat(openapi.statusCode()).isEqualTo(200);
        assertThat(openapi.body()).contains("\"/api/${{ values.entities }}\"", "\"x-refresquito-source\"", "\"table:${{ values.entity }}\"");
{%- if values.processes %}
        // block processes
        assertThat(openapi.body()).contains("\"/api/${{ values.entities }}/{id}/review\"", "\"process:review\"");
{%- endif %}
{%- if (values.buckets | length) > 0 %}
        // block s3
        assertThat(openapi.body()).contains("\"bucket:${{ values.buckets[0] }}\"");
{%- endif %}
{%- if (values.sites | length) > 0 %}
        // block dms
        assertThat(openapi.body()).contains("\"site:${{ values.sites[0] }}\"");
{%- endif %}
{%- if values.flows %}
        // block flows
        assertThat(openapi.body()).contains("\"flow:new-${{ values.entity }}\"");
{%- endif %}
    }

    /**
     * openapi.json of this folder is what the service publishes: the web generates its types from it (npm run gen:api),
     * the catalog of Backstage reads it. RQ_UPDATE_OPENAPI=1 writes it again after a change of the API.
     */
    @Test
    void the_openapi_file_is_what_the_service_publishes() throws Exception {
        String published = HTTP.send(HttpRequest.newBuilder(URI.create("http://127.0.0.1:" + port + "/api/openapi.json")).build(),
                HttpResponse.BodyHandlers.ofString()).body();
        String pretty = JSON.writerWithDefaultPrettyPrinter().writeValueAsString(JSON.readTree(published)) + "\n";
        java.nio.file.Path file = java.nio.file.Path.of("openapi.json");
        if ("1".equals(System.getenv("RQ_UPDATE_OPENAPI"))) {
            java.nio.file.Files.writeString(file, pretty);
        }
        // compared as JSON (not as text): the same document whatever the order of its keys or its spaces
        assertThat(java.nio.file.Files.exists(file) ? JSON.readTree(java.nio.file.Files.readString(file)) : null)
                .as("openapi.json is not what the service publishes: RQ_UPDATE_OPENAPI=1 mvn test, and commit it")
                .isEqualTo(JSON.readTree(pretty));
    }
}
