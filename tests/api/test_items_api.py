"""
Test API Items – solo HTTP via TestClient, nessun server reale.
Endpoint sotto /api/v1/items.
"""

import pytest
from fastapi.testclient import TestClient


def test_post_items_returns_201_created(client: TestClient) -> None:
    """POST /api/v1/items crea un item e ritorna 201 con body (id, name, description)."""
    response = client.post(
        "/api/v1/items",
        json={"name": "Test Item", "description": "A test"},
    )
    assert response.status_code == 201
    data = response.json()
    assert "id" in data
    assert data["name"] == "Test Item"
    assert data["description"] == "A test"
    assert isinstance(data["id"], int)
    assert data["id"] >= 1


def test_get_items_returns_200_and_list(seeded_items, client: TestClient) -> None:
    """GET /api/v1/items ritorna 200 e lista di item (dati da fixture + POST)."""
    client.post("/api/v1/items", json={"name": "One", "description": ""})
    client.post("/api/v1/items", json={"name": "Two", "description": "Second"})
    response = client.get("/api/v1/items")
    assert response.status_code == 200
    items = response.json()
    assert isinstance(items, list)
    names = {i["name"] for i in items}
    assert "test item" in names
    assert "One" in names
    assert "Two" in names
    for i in items:
        assert "id" in i and "name" in i and "description" in i


def test_get_item_by_id_returns_200_when_exists(client: TestClient) -> None:
    """GET /api/v1/items/{id} ritorna 200 e item quando esiste."""
    create = client.post("/api/v1/items", json={"name": "Found", "description": "x"})
    assert create.status_code == 201
    item_id = create.json()["id"]
    response = client.get(f"/api/v1/items/{item_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == item_id
    assert data["name"] == "Found"
    assert data["description"] == "x"


def test_get_item_by_id_returns_404_when_not_exists(client: TestClient) -> None:
    """GET /api/v1/items/{id} ritorna 404 quando la risorsa non esiste (REST best practice)."""
    response = client.get("/api/v1/items/99999")
    assert response.status_code == 404
    body = response.json()
    assert "detail" in body
    assert "99999" in body["detail"] or "not found" in body["detail"].lower()


def test_get_item_by_id_returns_422_when_id_invalid(client: TestClient) -> None:
    """GET /api/v1/items/{id} con id <= 0 ritorna 422."""
    assert client.get("/api/v1/items/0").status_code == 422
    assert client.get("/api/v1/items/-1").status_code == 422


def test_create_item_returns_422_when_name_empty(client: TestClient) -> None:
    """POST /api/v1/items con name vuoto ritorna 422."""
    response = client.post("/api/v1/items", json={"name": "", "description": "x"})
    assert response.status_code == 422


def test_delete_item_returns_204_when_exists(client: TestClient) -> None:
    """DELETE /api/v1/items/{id} ritorna 204 quando l'item esiste."""
    create = client.post("/api/v1/items", json={"name": "ToDelete", "description": ""})
    assert create.status_code == 201
    item_id = create.json()["id"]
    response = client.delete(f"/api/v1/items/{item_id}")
    assert response.status_code == 204
    assert response.content == b""
    assert client.get(f"/api/v1/items/{item_id}").status_code == 404


def test_delete_item_returns_404_when_not_exists(client: TestClient) -> None:
    """DELETE /api/v1/items/{id} ritorna 404 quando la risorsa non esiste (REST best practice)."""
    response = client.delete("/api/v1/items/99999")
    assert response.status_code == 404
    assert "detail" in response.json()
