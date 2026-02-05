"""
Test background tasks: response immediata e task registrato/eseguito.
Uso TestClient (fixture da conftest), mock della funzione di background, nessun sleep reale.
"""

from unittest.mock import patch

import pytest
from fastapi.testclient import TestClient


def test_post_items_response_immediate_and_background_task_executed(client: TestClient) -> None:
    """La response HTTP è immediata (201) e il background task viene eseguito dopo la response."""
    with patch("app.api.v1.items.on_item_created") as mock_on_item_created:
        response = client.post(
            "/api/v1/items",
            json={"name": "BgTask", "description": "Test"},
        )
        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "BgTask"
        assert "id" in data
        mock_on_item_created.assert_called_once_with(data["id"], "BgTask")


def test_background_task_does_not_block_response(client: TestClient) -> None:
    """Il task in background non blocca la risposta: il body è disponibile subito."""
    with patch("app.api.v1.items.on_item_created") as mock_on_item_created:
        response = client.post(
            "/api/v1/items",
            json={"name": "NoBlock", "description": ""},
        )
        assert response.status_code == 201
        assert response.json()["name"] == "NoBlock"
        assert mock_on_item_created.called
