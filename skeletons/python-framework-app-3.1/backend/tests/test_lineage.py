"""What each operation reads and writes, in the OpenAPI (refresquito-fastapi 3.1.2): the data catalog draws it."""

from ${{ values.name }}.main import app


def test_the_openapi_says_what_each_operation_reads_and_writes() -> None:
    paths = app.openapi()["paths"]
    assert paths["/api/${{ values.entities }}"]["get"]["x-refresquito-source"] == ["table:${{ values.entity }}"]
    assert paths["/api/${{ values.entities }}"]["post"]["x-refresquito-target"] == ["table:${{ values.entity }}"]
{%- if values.processes %}
    assert paths["/api/${{ values.entities }}/{${{ values.entity }}_id}/review"]["post"]["x-refresquito-target"] == ["process:review"]
{%- endif %}
{%- if values.flows %}
    assert paths["/api/${{ values.entities }}/{${{ values.entity }}_id}/welcome"]["post"]["x-refresquito-target"] == ["flow:new-${{ values.entity }}"]
{%- endif %}
{%- if (values.buckets | length) > 0 %}
    assert paths["/api/${{ values.entities }}/{${{ values.entity }}_id}/files"]["get"]["x-refresquito-source"] == ["bucket:${{ values.buckets[0] }}"]
{%- endif %}
{%- if (values.sites | length) > 0 %}
    assert paths["/api/${{ values.entities }}/{${{ values.entity }}_id}/documents"]["post"]["x-refresquito-target"] == ["site:${{ values.sites[0] }}"]
{%- endif %}
