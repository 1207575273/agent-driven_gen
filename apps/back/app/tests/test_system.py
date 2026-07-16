"""当前进程资源指标接口测试(只走 GET)。"""

from httpx import AsyncClient


async def test_should_return_process_stats(client: AsyncClient) -> None:
    resp = await client.get("/api/v1/system/stats")

    assert resp.status_code == 200
    body = resp.json()
    # 字段齐全且在合理范围
    assert set(body) == {"cpu_percent", "mem_rss", "mem_percent", "mem_total"}
    assert 0.0 <= body["cpu_percent"] <= 100.0
    assert 0.0 <= body["mem_percent"] <= 100.0
    assert body["mem_total"] > 0
    # 本进程 RSS 必然占用一部分, 且不超过系统总内存
    assert 0 < body["mem_rss"] <= body["mem_total"]
