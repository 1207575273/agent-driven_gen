"""Item 接口集成测试(只走 GET / POST)。"""

from httpx import AsyncClient


async def test_should_create_item_when_payload_valid(client: AsyncClient) -> None:
    resp = await client.post("/api/v1/items", json={"name": "widget", "quantity": 3})

    assert resp.status_code == 201
    body = resp.json()
    assert body["name"] == "widget"
    assert body["quantity"] == 3
    assert body["id"] >= 1


async def test_should_list_created_items(client: AsyncClient) -> None:
    await client.post("/api/v1/items", json={"name": "a"})
    await client.post("/api/v1/items", json={"name": "b"})

    resp = await client.get("/api/v1/items")

    assert resp.status_code == 200
    assert len(resp.json()) == 2


async def test_should_return_404_when_item_missing(client: AsyncClient) -> None:
    resp = await client.get("/api/v1/items/9999")

    assert resp.status_code == 404


async def test_should_update_item_via_post(client: AsyncClient) -> None:
    created = (await client.post("/api/v1/items", json={"name": "old"})).json()

    resp = await client.post(f"/api/v1/items/{created['id']}/update", json={"name": "new", "quantity": 5})

    assert resp.status_code == 200
    body = resp.json()
    assert body["name"] == "new"
    assert body["quantity"] == 5


async def test_should_delete_item_via_post_then_report_missing(client: AsyncClient) -> None:
    created = (await client.post("/api/v1/items", json={"name": "temp"})).json()

    delete_resp = await client.post(f"/api/v1/items/{created['id']}/delete")
    get_resp = await client.get(f"/api/v1/items/{created['id']}")

    assert delete_resp.status_code == 200
    assert delete_resp.json() == {"success": True}
    assert get_resp.status_code == 404


async def test_should_reject_invalid_payload_when_name_empty(client: AsyncClient) -> None:
    resp = await client.post("/api/v1/items", json={"name": ""})

    assert resp.status_code == 422
