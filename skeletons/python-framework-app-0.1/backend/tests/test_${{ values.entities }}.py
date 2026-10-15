import pytest
from refresquito_fastapi.testing import assert_problem

pytestmark = pytest.mark.anyio
REX = {"name": "Rex", "category": "tools", "start_date": "2022-05-01"}


async def create(client, admin, **fields) -> dict:
    response = await client.post("/api/${{ values.entities }}", json={**REX, **fields}, headers=admin)
    assert response.status_code == 201, response.text
    return response.json()


async def test_admin_creates_a_${{ values.entity }}(client, admin):
    ${{ values.entity }} = await create(client, admin)
    assert ${{ values.entity }}["id"] == 1 and ${{ values.entity }}["name"] == "Rex" and ${{ values.entity }}["category"] == "tools"
    assert ${{ values.entity }}["status"] == "active" and ${{ values.entity }}["start_date"] == "2022-05-01"
    assert ${{ values.entity }}["created_by"] == "ana" and ${{ values.entity }}["created_at"]


async def test_viewer_reads_but_does_not_write(client, admin, viewer):
    ${{ values.entity }} = await create(client, admin)
    assert (await client.get(f"/api/${{ values.entities }}/{${{ values.entity }}['id']}", headers=viewer)).json()["name"] == "Rex"
    assert (await client.get("/api/${{ values.entities }}", headers=viewer)).json()["total"] == 1
    assert_problem(await client.post("/api/${{ values.entities }}", json=REX, headers=viewer), 403, "forbidden")
    assert_problem(await client.put(f"/api/${{ values.entities }}/{${{ values.entity }}['id']}", json=REX, headers=viewer), 403, "forbidden")
    assert_problem(await client.delete(f"/api/${{ values.entities }}/{${{ values.entity }}['id']}", headers=viewer), 403, "forbidden")


async def test_without_a_token_or_a_${{ values.name }}_role_nothing_is_readable(client, tokens):
    assert_problem(await client.get("/api/${{ values.entities }}"), 401, "unauthorized")
    assert_problem(await client.get("/api/${{ values.entities }}", headers=tokens.headers("eve", roles=["other"])), 403, "forbidden")


async def test_two_${{ values.entities }}_cannot_share_a_name(client, admin):
    await create(client, admin)
    body = assert_problem(await client.post("/api/${{ values.entities }}", json=REX, headers=admin), 409, "${{ values.entity }}_name_taken")
    assert "Rex" in body["detail"]


async def test_update(client, admin):
    ${{ values.entity }} = await create(client, admin)
    await create(client, admin, name="Tom", category="books")
    changed = await client.put(f"/api/${{ values.entities }}/{${{ values.entity }}['id']}", json={**REX, "status": "closed"}, headers=admin)
    assert changed.status_code == 200 and changed.json()["status"] == "closed"
    # its own name is not a conflict, somebody else's is
    assert_problem(
        await client.put(f"/api/${{ values.entities }}/{${{ values.entity }}['id']}", json={**REX, "name": "Tom"}, headers=admin), 409, "${{ values.entity }}_name_taken"
    )
    assert_problem(await client.put("/api/${{ values.entities }}/999", json=REX, headers=admin), 404, "not_found")


async def test_delete(client, admin):
    ${{ values.entity }} = await create(client, admin)
    assert (await client.delete(f"/api/${{ values.entities }}/{${{ values.entity }}['id']}", headers=admin)).status_code == 204
    assert_problem(await client.get(f"/api/${{ values.entities }}/{${{ values.entity }}['id']}", headers=admin), 404, "not_found")
    assert_problem(await client.delete(f"/api/${{ values.entities }}/{${{ values.entity }}['id']}", headers=admin), 404, "not_found")


async def test_list_is_sorted_filtered_and_paged(client, admin):
    for name, category, status in [
        ("Rex", "tools", "active"),
        ("Tom", "books", "closed"),
        ("Ada", "books", "active"),
        ("Bob", "tools", "pending"),
    ]:
        await create(client, admin, name=name, category=category, status=status)
    everything = (await client.get("/api/${{ values.entities }}", headers=admin)).json()
    assert [p["name"] for p in everything["items"]] == ["Ada", "Bob", "Rex", "Tom"]
    cats = (await client.get("/api/${{ values.entities }}", params={"category": "books"}, headers=admin)).json()
    assert [p["name"] for p in cats["items"]] == ["Ada", "Tom"]
    active = (await client.get("/api/${{ values.entities }}", params={"status": "active"}, headers=admin)).json()
    assert [p["name"] for p in active["items"]] == ["Ada", "Rex"]
    page = (await client.get("/api/${{ values.entities }}", params={"page": 2, "size": 3}, headers=admin)).json()
    assert [p["name"] for p in page["items"]] == ["Tom"] and page["total"] == 4


@pytest.mark.parametrize(
    ("fields", "field"),
    [
        ({"name": "   "}, "name"),
        ({"category": ""}, "category"),
        ({"status": "lost"}, "status"),
        ({"start_date": "2999-01-01"}, "start_date"),
        ({"name": "x" * 81}, "name"),
    ],
)
async def test_invalid_${{ values.entities }}_are_rejected_with_the_field(client, admin, fields, field):
    body = assert_problem(await client.post("/api/${{ values.entities }}", json={**REX, **fields}, headers=admin), 422, "validation_error")
    assert body["errors"][0]["field"] == field


async def test_names_are_trimmed(client, admin):
    assert (await create(client, admin, name="  Rex  "))["name"] == "Rex"


async def test_ready_checks_the_database(client):
    ready = await client.get("/health/ready")
    assert ready.status_code == 200 and ready.json()["checks"]["database"] == "ok"


async def test_openapi_is_published_under_api(client):
    spec = (await client.get("/api/openapi.json")).json()
    assert spec["info"]["title"] == "${{ values.title }} API" and "/api/${{ values.entities }}/{${{ values.entity }}_id}" in spec["paths"]
