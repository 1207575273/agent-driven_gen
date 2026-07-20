"""Item 接口集成测试(只走 GET / POST)。"""

from httpx import AsyncClient


async def test_should_create_item_when_payload_valid(client: AsyncClient) -> None:
    resp = await client.post("/api/v1/items", json={"name": "widget", "quantity": 3})

    assert resp.status_code == 201
    body = resp.json()
    assert body["name"] == "widget"
    assert body["quantity"] == 3
    assert body["id"] >= 1


async def test_should_list_created_items_as_page(client: AsyncClient) -> None:
    await client.post("/api/v1/items", json={"name": "a"})
    await client.post("/api/v1/items", json={"name": "b"})

    resp = await client.get("/api/v1/items")

    assert resp.status_code == 200
    body = resp.json()
    assert body["total"] == 2
    assert len(body["items"]) == 2
    assert body["limit"] == 20
    assert body["offset"] == 0


async def test_should_paginate_items(client: AsyncClient) -> None:
    for i in range(3):
        await client.post("/api/v1/items", json={"name": f"n{i}"})

    page1 = (await client.get("/api/v1/items?limit=2&offset=0")).json()
    page2 = (await client.get("/api/v1/items?limit=2&offset=2")).json()

    assert page1["total"] == 3
    assert page2["total"] == 3
    assert len(page1["items"]) == 2
    assert len(page2["items"]) == 1
    ids1 = {it["id"] for it in page1["items"]}
    ids2 = {it["id"] for it in page2["items"]}
    assert ids1.isdisjoint(ids2)


async def test_should_reject_out_of_range_pagination(client: AsyncClient) -> None:
    assert (await client.get("/api/v1/items?limit=0")).status_code == 422
    assert (await client.get("/api/v1/items?limit=101")).status_code == 422
    assert (await client.get("/api/v1/items?offset=-1")).status_code == 422


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
