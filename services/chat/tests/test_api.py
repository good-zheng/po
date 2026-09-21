import pytest
from fastapi.testclient import TestClient

from app.main import create_app
from app.store import ItemStore, get_store


@pytest.fixture
def store() -> ItemStore:
    return ItemStore()


@pytest.fixture
def client(store: ItemStore) -> TestClient:
    app = create_app()
    app.dependency_overrides[get_store] = lambda: store
    return TestClient(app)


def test_health(client: TestClient) -> None:
    response = client.get("/api/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_item_crud_flow(client: TestClient) -> None:
    payload = {"name": "耳机", "description": "降噪耳机", "price": 899.0, "in_stock": True}

    created = client.post("/api/items", json=payload)
    assert created.status_code == 201
    body = created.json()
    assert body["id"] == 1
    assert body["name"] == payload["name"]

    fetched = client.get(f"/api/items/{body['id']}")
    assert fetched.status_code == 200
    assert fetched.json()["price"] == payload["price"]

    patched = client.patch(f"/api/items/{body['id']}", json={"price": 799.0})
    assert patched.status_code == 200
    assert patched.json()["price"] == 799.0
    assert patched.json()["name"] == payload["name"]

    listed = client.get("/api/items", params={"q": "耳机"})
    assert listed.status_code == 200
    assert len(listed.json()) == 1

    deleted = client.delete(f"/api/items/{body['id']}")
    assert deleted.status_code == 204

    missing = client.get(f"/api/items/{body['id']}")
    assert missing.status_code == 404


def test_item_not_found(client: TestClient) -> None:
    assert client.get("/api/items/999").status_code == 404
    assert client.patch("/api/items/999", json={"price": 1.0}).status_code == 404
    assert client.delete("/api/items/999").status_code == 404


def test_item_validation(client: TestClient) -> None:
    assert client.post("/api/items", json={"name": "", "price": 10}).status_code == 422
    assert client.post("/api/items", json={"name": "x", "price": -1}).status_code == 422
