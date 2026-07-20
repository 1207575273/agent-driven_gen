"""request-id 中间件测试: 生成与透传, 并回写响应头。"""

from httpx import AsyncClient


async def test_should_generate_request_id_when_absent(client: AsyncClient) -> None:
    resp = await client.get("/api/v1/health")

    request_id = resp.headers.get("X-Request-ID")
    assert request_id  # 未带则服务端生成一个非空 id
    assert len(request_id) >= 8


async def test_should_echo_request_id_when_provided(client: AsyncClient) -> None:
    resp = await client.get("/api/v1/health", headers={"X-Request-ID": "trace-abc-123"})

    # 入站带 id 则原样透传, 便于跨服务串联
    assert resp.headers.get("X-Request-ID") == "trace-abc-123"
