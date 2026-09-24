import importlib
import os
import sys
from concurrent.futures import ThreadPoolExecutor
from urllib.parse import parse_qs, urlsplit

import pytest
from fastapi.testclient import TestClient


@pytest.fixture
def api(tmp_path, monkeypatch):
    monkeypatch.setenv("DATABASE_PATH", str(tmp_path / "test.db"))
    monkeypatch.setenv("ADMIN_KEY", "test-admin-" + "a" * 32)
    monkeypatch.setenv("INGEST_KEY", "test-ingest-" + "b" * 32)
    if "app" in sys.modules:
        module = importlib.reload(sys.modules["app"])
    else:
        module = importlib.import_module("app")
    with TestClient(module.app) as client:
        yield client, module


def campaign(client, **overrides):
    return client.post("/api/campaigns", headers={"X-Admin-Key": os.environ["ADMIN_KEY"]},
        json={"name": "Launch", "destination": "https://example.com/page?x=1&utm_source=old#offer",
              "source": "linkedin", "medium": "social", "campaign": "launch",
              "spend_cents": 10000, **overrides})


def click(client, cid):
    result = client.get(f"/r/{cid}", follow_redirects=False)
    assert result.status_code == 302
    return parse_qs(urlsplit(result.headers["location"]).query)


def conversion(client, click_id, event="order_123456", revenue=25000):
    return client.post("/api/conversions", headers={"X-Ingest-Key": os.environ["INGEST_KEY"]},
                       json={"event_id": event, "click_id": click_id, "revenue_cents": revenue})


def test_auth_boundaries(api):
    client, _ = api
    assert client.get("/api/campaigns").status_code == 401
    assert client.get("/api/export.csv").status_code == 401
    assert client.get("/api/campaigns", headers={"X-Admin-Key": os.environ["INGEST_KEY"]}).status_code == 401
    assert client.post("/api/conversions", json={"event_id": "order_123456",
        "click_id": "x" * 24, "revenue_cents": 0}).status_code == 401


def test_full_attribution_and_replay(api):
    client, _ = api
    cid = campaign(client).json()["id"]
    params = click(client, cid)
    assert params["utm_source"] == ["linkedin"] and params["x"] == ["1"]
    token = params["cl_click"][0]
    assert conversion(client, token).status_code == 201
    assert conversion(client, token).json()["replayed"] is True
    assert conversion(client, token, revenue=1).status_code == 409
    assert conversion(client, token, event="order_second").status_code == 201
    row = client.get("/api/campaigns", headers={"X-Admin-Key": os.environ["ADMIN_KEY"]}).json()["campaigns"][0]
    assert (row["clicks"], row["conversions"], row["converted_clicks"]) == (1, 2, 1)
    assert row["revenue_cents"] == 50000 and row["roas"] == 5 and row["conversion_rate"] == 1


def test_concurrent_retries(api):
    client, _ = api
    token = click(client, campaign(client).json()["id"])["cl_click"][0]
    with ThreadPoolExecutor(max_workers=6) as pool:
        results = list(pool.map(lambda _: conversion(client, token).status_code, range(6)))
    assert results.count(201) == 1 and results.count(200) == 5


def test_invalid_and_expired_click(api):
    client, module = api
    assert conversion(client, "unknown" * 4).status_code == 422
    token = click(client, campaign(client).json()["id"])["cl_click"][0]
    with module.db() as con:
        con.execute("UPDATE clicks SET created_at=datetime('now','-31 days') WHERE id=?", (token,))
    assert conversion(client, token).status_code == 422
    assert client.get("/r/missing").status_code == 404


@pytest.mark.parametrize("url", ["javascript:alert(1)", "http://example.com", "https://user:pass@example.com", "https://[invalid", "https://example.com:wrong"])
def test_destination_validation(api, url):
    assert campaign(api[0], destination=url).status_code == 422


def test_zero_denominator_and_csv(api):
    client, _ = api
    assert campaign(client, name="=SUM(A1)", spend_cents=0).status_code == 201
    headers = {"X-Admin-Key": os.environ["ADMIN_KEY"]}
    row = client.get("/api/campaigns", headers=headers).json()["campaigns"][0]
    assert row["roas"] is None and row["conversion_rate"] is None
    assert "'=SUM(A1)" in client.get("/api/export.csv", headers=headers).text
    assert client.get("/").headers["content-security-policy"]


def test_budget_and_size_validation(api):
    client, _ = api
    assert campaign(client, spend_cents=-1).status_code == 422
    assert campaign(client, source="Linked In").status_code == 422
    assert client.post("/api/campaigns", content="x" * 9000).status_code == 413
