import pytest
from fastapi.testclient import TestClient
from bson import ObjectId
from datetime import datetime
from main import app
from database import clients_collection

@pytest.fixture
def client():
    with TestClient(app) as test_client:
        yield test_client

def test_create_client(client):
    payload = {"name": "TestService"}
    response = client.post("/clients/", json=payload)

    assert response.status_code == 201

    data = response.json()
    assert set(data.keys()) == {"id", "name", "active", "created_at"}
    assert data["name"] == "TestService"
    assert data["active"] is True
    assert ObjectId.is_valid(data["id"])

    created_at = datetime.fromisoformat(data["created_at"])
    assert created_at.tzinfo is not None

    saved_client = clients_collection.find_one(
        {"_id": ObjectId(data["id"])}
    )

    assert saved_client is not None
    assert saved_client["name"] == "TestService"

    clients_collection.delete_one({"_id": ObjectId(data["id"])})


@pytest.mark.parametrize("payload", [
    {},
    {"name": ""},
    {"name": "   "},
    {"name": "TestService", "active": False}
])
def test_create_client_invalid_input(client, payload):
    response = client.post("/clients/", json=payload)
    assert response.status_code == 422


def test_get_clients(client):
    create_response = client.post(
        "/clients/",
        json={"name": "GetTestService"}
    )

    assert create_response.status_code == 201

    created_data = create_response.json()
    created_id = created_data["id"]

    try:
        response = client.get("/clients/")

        assert response.status_code == 200

        data = response.json()
        assert isinstance(data, list)

        matching_clients = [
            item for item in data if item["id"] == created_id
        ]

        assert len(matching_clients) == 1

        retrieved_client = matching_clients[0]

        assert set(retrieved_client.keys()) == {
            "id", "name", "active", "created_at"
        }

        assert retrieved_client["name"] == "GetTestService"
        assert retrieved_client["active"] is True
        assert ObjectId.is_valid(retrieved_client["id"])

        datetime.fromisoformat(retrieved_client["created_at"])

    finally:
        clients_collection.delete_one(
            {"_id": ObjectId(created_id)}
        )
