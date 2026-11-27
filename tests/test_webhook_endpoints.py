import pytest
from main import app
from fastapi.testclient import TestClient
from datetime import datetime, timezone
from database import clients_collection, api_keys_collection, webhook_endpoints_collection
from utils import api_key_utils
from bson import ObjectId

@pytest.fixture
def client():
    with TestClient(app) as test_client:
        yield test_client


@pytest.fixture
def webhook_test_data():
    client_data = {
        "name": "Webhook Test Client",
        "active": True,
        "created_at": datetime.now(timezone.utc)
    }

    client_result = clients_collection.insert_one(client_data)
    client_id = client_result.inserted_id

    api_key = api_key_utils.generate_api_key()

    api_key_data = {
        "client_id": client_id,
        "name": client_data["name"],
        "key_hash": api_key_utils.hash_api_key(api_key),
        "active": True,
        "created_at": datetime.now(timezone.utc)
    }

    api_keys_collection.insert_one(api_key_data)

    yield {
        "client_id": client_id,
        "api_key": api_key
    }

    webhook_endpoints_collection.delete_many({"client_id":client_id})
    api_keys_collection.delete_many({"client_id":client_id})
    clients_collection.delete_one({"_id":client_id})


def test_register_endpoint(client, webhook_test_data):
    payload = {
        "url": "https://example.com/webhooks/orders",
        "subscribed_events": [
            "order.created",
            "order.cancelled"
        ]
    }

    headers = {
        "Authorization": f"Bearer {webhook_test_data['api_key']}"
    }   

    response = client.post("/webhook-endpoints/", json=payload, headers=headers)
    assert response.status_code == 201

    data = response.json()
    assert set(data.keys()) == {"id", "url", "subscribed_events", "active", "created_at", "signing_secret"}
    assert payload["url"] == data["url"]
    assert payload["subscribed_events"] == data["subscribed_events"]
    assert data["active"] is True
    assert ObjectId.is_valid(data["id"])

    created_at = datetime.fromisoformat(data["created_at"])
    assert created_at.tzinfo is not None

    webhook_data = webhook_endpoints_collection.find_one({"_id": ObjectId(data["id"])})

    assert webhook_data is not None
    assert webhook_data["client_id"] == webhook_test_data["client_id"]
    assert webhook_data["url"] == payload["url"]    
    assert webhook_data["subscribed_events"] == payload["subscribed_events"]
    assert webhook_data["active"] is True


def test_register_duplicate_endpoint(client, webhook_test_data):
    payload1 = {
        "url": "https://example.com/webhooks/orders",
        "subscribed_events": [
            "order.created"
        ]
    }

    headers = {
        "Authorization": f"Bearer {webhook_test_data['api_key']}"
    }   

    response1 = client.post("/webhook-endpoints/", json=payload1, headers=headers)
    assert response1.status_code == 201
    data1 = response1.json()

    payload2 = {
        "url": "https://example.com/webhooks/orders",
        "subscribed_events": [
            "order.cancelled"
        ]
    }

    response2 = client.post("/webhook-endpoints/", json=payload2, headers=headers)
    assert response2.status_code == 200
    data2 = response2.json()

    assert set(data2.keys()) == {"id", "url", "subscribed_events", "active", "created_at"}
    assert data1["id"] == data2["id"]
    assert data1["url"] == data2["url"]
    assert data1["created_at"] == data2["created_at"]
    assert data2["subscribed_events"] == ["order.created","order.cancelled"]
    assert data2["active"] is True

    webhook_data = webhook_endpoints_collection.find_one({"_id": ObjectId(data2["id"])})

    assert webhook_data is not None
    assert str(webhook_data["_id"]) == data2["id"]
    assert webhook_data["client_id"] == webhook_test_data["client_id"]
    assert webhook_data["url"] == payload2["url"]    
    assert webhook_data["subscribed_events"] == ["order.created", "order.cancelled"]
    assert webhook_data["active"] is True

    assert webhook_endpoints_collection.count_documents({"client_id":webhook_data["client_id"], "url":payload1["url"]}) == 1


def test_register_endpoint_with_empty_events(client, webhook_test_data):
    payload = {
        "url": "https://example.com/webhooks/orders",
        "subscribed_events": []
    }

    headers = {
        "Authorization": f"Bearer {webhook_test_data['api_key']}"
    }   

    response = client.post("/webhook-endpoints/", json=payload, headers=headers)
    assert response.status_code == 201

    data = response.json()
    assert set(data.keys()) == {"id", "url", "subscribed_events", "active", "created_at", "signing_secret"}
    assert data["url"] == payload["url"]
    assert data["subscribed_events"] == []
    assert data["active"] is True
    assert ObjectId.is_valid(data["id"])

    created_at = datetime.fromisoformat(data["created_at"])
    assert created_at.tzinfo is not None

    webhook_data = webhook_endpoints_collection.find_one({"_id": ObjectId(data["id"])})

    assert webhook_data is not None
    assert webhook_data["client_id"] == webhook_test_data["client_id"]
    assert webhook_data["url"] == payload["url"]    
    assert webhook_data["subscribed_events"] == payload["subscribed_events"]
    assert webhook_data["active"] is True


def test_get_all_webhook_endpoints(client, webhook_test_data):
    payloads = [
        {
            "url": "https://example.com/webhooks/orders",
            "subscribed_events": ["order.created"]
        },
        {
            "url": "https://example.com/webhooks/payments",
            "subscribed_events": ["payment.completed"]
        }
    ]

    headers = {
        "Authorization": f"Bearer {webhook_test_data['api_key']}"
    }

    for payload in payloads: 
        response = client.post("/webhook-endpoints/", json=payload, headers=headers)
        assert response.status_code == 201

    response = client.get("/webhook-endpoints/", headers=headers)

    assert response.status_code == 200

    data = response.json()

    assert len(data) == 2

    returned_urls = {endpoint["url"] for endpoint in data}
    expected_urls = {payload["url"] for payload in payloads}

    assert returned_urls == expected_urls


def test_get_webhook_endpoint_by_id(client, webhook_test_data):
    payload = {
        "url": "https://example.com/webhooks/orders",
        "subscribed_events": ["order.created", "order.cancelled"]
    }

    headers = {
        "Authorization": f"Bearer {webhook_test_data['api_key']}"
    }

    create_response = client.post("/webhook-endpoints/", json=payload, headers=headers)

    endpoint_id = create_response.json()["id"]

    response = client.get(f"/webhook-endpoints/{endpoint_id}", headers=headers)

    assert response.status_code == 200

    data = response.json()

    assert data["id"] == endpoint_id
    assert data["url"] == payload["url"]
    assert data["subscribed_events"] == payload["subscribed_events"]
    assert data["active"] is True


def test_delete_webhook_endpoint(client, webhook_test_data):
    payload = {
        "url": "https://example.com/webhooks/orders",
        "subscribed_events": ["order.created"]
    }

    headers = {
        "Authorization": f"Bearer {webhook_test_data['api_key']}"
    }

    create_response = client.post("/webhook-endpoints/", json=payload, headers=headers)

    endpoint_id = create_response.json()["id"]

    response = client.delete(f"/webhook-endpoints/{endpoint_id}", headers=headers)

    assert response.status_code == 204

    endpoint = webhook_endpoints_collection.find_one({"_id": ObjectId(endpoint_id)})

    assert endpoint is None