"""Integration tests for FastAPI endpoints."""

import pytest
from httpx import ASGITransport, AsyncClient

from aerosearch.api.main import app


@pytest.mark.asyncio
async def test_api_health() -> None:
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.get("/health")
        assert resp.status_code == 200
        assert resp.json() == {"status": "ok", "service": "aerosearch"}


@pytest.mark.asyncio
async def test_api_indexing_and_search() -> None:
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # Index custom doc
        doc_data = {
            "id": "custom-test-1",
            "title": "Quantum Teleportation Protocols",
            "content": "Entangled photons enable secure quantum teleportation across fiber optic links.",
            "tags": ["quantum", "physics"],
            "metadata": {"test": True},
        }
        res_post = await client.post("/api/v1/index/documents", json=doc_data)
        assert res_post.status_code == 201

        # Search for quantum
        res_search = await client.get("/api/v1/search?q=quantum&limit=5")
        assert res_search.status_code == 200
        data = res_search.json()
        assert data["total_hits"] >= 1
        assert any(r["doc_id"] == "custom-test-1" for r in data["results"])

        # Autocomplete
        res_auto = await client.get("/api/v1/autocomplete?prefix=quant")
        assert res_auto.status_code == 200
        auto_data = res_auto.json()
        terms = [item["term"] for item in auto_data["suggestions"]]
        assert any("quant" in t for t in terms)

        # Stats
        res_stats = await client.get("/api/v1/stats")
        assert res_stats.status_code == 200
        stats_data = res_stats.json()
        assert stats_data["total_documents"] > 0

        # Benchmark
        res_bench = await client.get("/api/v1/benchmark?q=teleportation")
        assert res_bench.status_code == 200
        bench_data = res_bench.json()
        assert "speedup_factor" in bench_data
