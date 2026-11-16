import pytest
from fastapi import FastAPI, Depends
from fastapi.testclient import TestClient
from dependencies.auth import get_authenticated_client
from database import clients_collection, api_keys_collection
from utils.api_key_utils import generate_api_key, hash_api_key
from datetime import datetime, timezone

app = FastAPI()

@app.get("/test-auth")
def protected_test_endpoint(client=Depends(get_authenticated_client)):
    return {"client_name": client["name"]}

@pytest.fixture
def client():
    with TestClient(app) as test_client:
        yield test_client


@pytest.fixture
def auth_test_data():
    client_data = {
        "name": "AuthTestClient",
        "active": True,
        "created_at": datetime.now(timezone.utc)
    }

    client_result = clients_collection.insert_one(client_data)
    client_id = client_result.inserted_id

    api_key = generate_api_key()

    api_key_data = {
        "client_id": client_id,
        "name": "AuthTestClient",
        "key_hash": hash_api_key(api_key),
        "active": True,
        "created_at": client_data["created_at"]
    }

    api_keys_collection.insert_one(api_key_data)

    yield {
        "client_id": client_id,
        "api_key": api_key
    }

    api_keys_collection.delete_many({"client_id": client_id})
    clients_collection.delete_one({"_id": client_id})


def test_auth_valid_key(client, auth_test_data):
    response = client.get(
        "/test-auth",
        headers={"Authorization": f"Bearer {auth_test_data['api_key']}"}
    )

    assert response.status_code == 200
    assert response.json()["client_name"] == "AuthTestClient"


def test_auth_invalid_key(client):
    response = client.get(
        "/test-auth",
        headers={"Authorization": "Bearer invalid_key"}
    )

    assert response.status_code == 401


def test_auth_inactive_api_key(client, auth_test_data):
    api_keys_collection.update_one(
        {"client_id": auth_test_data["client_id"]},
        {"$set": {"active": False}}
    )

    response = client.get(
        "/test-auth",
        headers={"Authorization": f"Bearer {auth_test_data['api_key']}"}
    )

    assert response.status_code == 401


def test_auth_inactive_client(client, auth_test_data):
    clients_collection.update_one(
        {"_id": auth_test_data["client_id"]},
        {"$set": {"active": False}}
    )

    response = client.get(
        "/test-auth",
        headers={"Authorization": f"Bearer {auth_test_data['api_key']}"}
    )

    assert response.status_code == 401


def test_auth_missing_header(client):
    response = client.get("/test-auth")

    assert response.status_code == 401


def test_auth_invalid_scheme(client):
    response = client.get(
        "/test-auth",
        headers={"Authorization": "Basic abc123"}
    )

    assert response.status_code == 401


def test_auth_empty_bearer_token(client):
    response = client.get(
        "/test-auth",
        headers={"Authorization": "Bearer "}
    )

    assert response.status_code == 401
