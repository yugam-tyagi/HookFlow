import pytest
import hashlib
from fastapi.testclient import TestClient
from main import app
from database import clients_collection,api_keys_collection
from bson import ObjectId

@pytest.fixture
def client():
    with TestClient(app) as test_client:
        yield test_client

def test_generate_api_key(client):
    client_doc = clients_collection.find_one({"active":True})
    assert client_doc is not None
    client_id = client_doc["_id"]

    existing_key = api_keys_collection.find_one(
        {"client_id": client_id}
    )

    try:
        response = client.post(f"/clients/{client_id}/api-key")

        assert response.status_code == 201

        data = response.json()
        api_key = data["api_key"]

        assert isinstance (api_key,str)
        assert api_key.startswith("hf_live_")
        assert len(api_key)>len("hf_live_")

        api_key_hash = hashlib.sha256(api_key.encode()).hexdigest()
    
        api_key_data = api_keys_collection.find_one({"client_id":client_id})
        assert api_key_data is not None
        assert "api_key" not in api_key_data

        key_hash = api_key_data["key_hash"]
        assert api_key_hash == key_hash

    finally:
        if existing_key is not None:
            api_keys_collection.replace_one(
                {"client_id": client_id},
                existing_key
            )
        else:
            api_keys_collection.delete_one(
                {"client_id": client_id}
            )


def test_regenerate_api_key(client):
    client_doc = clients_collection.find_one({"active":True})
    assert client_doc is not None
    client_id = client_doc["_id"]

    existing_key = api_keys_collection.find_one(
        {"client_id": client_id}
    )

    try:
        response1 = client.post(f"/clients/{client_id}/api-key")

        assert response1.status_code == 201

        data1 = response1.json()
        api_key1 = data1["api_key"]

        response2 = client.post(f"/clients/{client_id}/api-key")

        assert response2.status_code == 201

        data2 = response2.json()
        api_key2 = data2["api_key"]

        assert api_key1 != api_key2
        assert api_key1.startswith("hf_live_")
        assert api_key2.startswith("hf_live_")

        old_key_hash = hashlib.sha256(api_key1.encode()).hexdigest()
        api_key_hash = hashlib.sha256(api_key2.encode()).hexdigest()
    
        api_key_data = api_keys_collection.find_one({"client_id":client_id})
        assert api_key_data is not None
        assert "api_key" not in api_key_data

        key_hash = api_key_data["key_hash"]
        assert old_key_hash != key_hash
        assert api_key_hash == key_hash

        count = api_keys_collection.count_documents({"client_id": client_id})
        assert count == 1

    finally:
        if existing_key is not None:
            api_keys_collection.replace_one(
                {"client_id": client_id},
                existing_key
            )
        else:
            api_keys_collection.delete_one(
                {"client_id": client_id}
            )


def test_generate_api_key_invalid_id(client):
    response = client.post("/clients/invalid_client_id/api-key")

    assert response.status_code == 400
    assert response.json()["detail"] == "Invalid client ID"


def test_generate_api_key_client_not_found(client):
    client_id = str(ObjectId())

    response = client.post(f"/clients/{client_id}/api-key")

    assert response.status_code == 404
    assert response.json()["detail"] == "Client doesn't exist"


def test_generate_api_key_inactive_client(client):
    client_doc = clients_collection.find_one({"active":True})
    assert client_doc is not None
    client_id = client_doc["_id"]
    original_status = client_doc["active"]

    clients_collection.update_one(
        {"_id": client_id},
        {"$set": {"active": False}}
    )

    try:
        response = client.post(f"/clients/{client_id}/api-key")

        assert response.status_code == 403
        assert response.json()["detail"] == "Client is inactive"

    finally:
        clients_collection.update_one(
            {"_id": client_id},
            {"$set": {"active": original_status}}
        )