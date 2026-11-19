import pytest
from main import app
from fastapi.testclient import TestClient
from datetime import datetime, timezone
from utils import api_key_utils
from bson import ObjectId
from repositories import webhook_endpoint_repository
from database import clients_collection, api_keys_collection, webhook_endpoints_collection, events_collection, deliveries_collection

@pytest.fixture
def client():
    with TestClient(app) as test_client:
        yield test_client


@pytest.fixture
def events_test_data():
    timestamp = datetime.now(timezone.utc)

    client_data = {
        "name": "Event Test Client",
        "active": True,
        "created_at": timestamp
    }

    client_result = clients_collection.insert_one(client_data)
    client_id = client_result.inserted_id

    api_key = api_key_utils.generate_api_key()

    api_key_data = {
        "client_id": client_id,
        "name": client_data["name"],
        "key_hash": api_key_utils.hash_api_key(api_key),
        "active": True,
        "created_at": timestamp
    }

    api_keys_collection.insert_one(api_key_data)

    yield {
        "client_id": client_id,
        "api_key": api_key
    }

    deliveries_collection.delete_many({"client_id":client_id})
    events_collection.delete_many({"client_id":client_id})
    webhook_endpoints_collection.delete_many({"client_id":client_id})
    api_keys_collection.delete_many({"client_id":client_id})
    clients_collection.delete_one({"_id":client_id})


def test_create_event_with_multiple_endpoints(client, events_test_data):
    url1 = "https://webhook-a.example.com/events"
    url2 = "https://webhook-b.example.com/events"
    url3 = "https://webhook-c.example.com/events"
    url4 = "https://webhook-d.example.com/events"

    subscribed_events1 = ["order.created"]
    subscribed_events2 = ["payment.completed"]

    webhook_endpoint_repository.upsert_webhook_endpoint(events_test_data['client_id'], url1, subscribed_events1)
    webhook_endpoint_repository.upsert_webhook_endpoint(events_test_data['client_id'], url2, subscribed_events1)
    webhook_endpoint_repository.upsert_webhook_endpoint(events_test_data['client_id'], url3, subscribed_events2)
    webhook_endpoint_repository.upsert_webhook_endpoint(events_test_data['client_id'], url4, subscribed_events1)

    webhook_endpoints_collection.update_one(
        {"url": url4, "client_id": events_test_data['client_id']},
        {
            "$set":{
                "active": False
            }
        }
    )

    payload = {
        "event_type": "order.created",
        "payload": {
            "order_id": "ORD-1001",
            "customer_id": "CUST-501",
            "amount": 2499.99,
            "currency": "INR",
            "payment_status": "PAID",
            "items": [
            {
                "product_id": "PROD-101",
                "name": "Wireless Headphones",
                "quantity": 1,
                "price": 2499.99
            }
            ],
            "shipping_address": {
                "city": "Bangalore",
                "state": "Karnataka",
                "country": "India"
            }
        }
    }

    headers = {
        "Authorization": f"Bearer {events_test_data['api_key']}"
    }   

    response = client.post("/events/", json=payload, headers=headers)
    assert response.status_code == 202

    data = response.json()
    event_id = ObjectId(data["id"])
    assert data["event_type"] == payload["event_type"]
    assert data["created_at"] is not None

    assert events_collection.count_documents({"_id": event_id, "client_id": events_test_data["client_id"]}) == 1 

    event = events_collection.find_one({"_id": event_id, "client_id":events_test_data["client_id"]})

    assert event["event_type"] == payload["event_type"]
    assert event["payload"] == payload["payload"]

    assert deliveries_collection.count_documents({"event_id": event_id, "client_id":events_test_data["client_id"]}) == 2
    deliveries = deliveries_collection.find({"event_id": event_id, "client_id":events_test_data["client_id"]})

    count = 1

    actual_urls = set()

    for delivery in deliveries:
        assert delivery["event_id"] == event_id
        assert delivery["status"] == "pending"
        assert delivery["attempt_count"] == 0

        endpoint = webhook_endpoint_repository.get_webhook_endpoint_by_id(events_test_data["client_id"],delivery["endpoint_id"])
        actual_urls.add(endpoint["url"])

    assert actual_urls == {url1, url2}


def test_create_event_with_no_matching_endpoints(client, events_test_data):
    url = "https://webhook-a.example.com/events"
    subscribed_events = ["payment.completed"]
    webhook_endpoint_repository.upsert_webhook_endpoint(events_test_data['client_id'], url, subscribed_events)

    payload = {
        "event_type": "order.created",
        "payload": {
            "order_id": "ORD-1001",
            "customer_id": "CUST-501",
            "amount": 2499.99,
            "currency": "INR",
            "payment_status": "PAID",
            "items": [
            {
                "product_id": "PROD-101",
                "name": "Wireless Headphones",
                "quantity": 1,
                "price": 2499.99
            }
            ],
            "shipping_address": {
                "city": "Bangalore",
                "state": "Karnataka",
                "country": "India"
            }
        }
    }

    headers = {
        "Authorization": f"Bearer {events_test_data['api_key']}"
    }   

    response = client.post("/events/", json=payload, headers=headers)
    assert response.status_code == 202

    data = response.json()
    event_id = ObjectId(data["id"])
    assert data["event_type"] == payload["event_type"]
    assert data["created_at"] is not None

    assert events_collection.count_documents({"_id": event_id, "client_id": events_test_data["client_id"]}) == 1 
    event = events_collection.find_one({"_id": event_id, "client_id":events_test_data["client_id"]})

    assert event["event_type"] == payload["event_type"]
    assert event["payload"] == payload["payload"]

    assert deliveries_collection.count_documents({"event_id": event_id, "client_id":events_test_data["client_id"]}) == 0



@pytest.mark.parametrize("invalid_payload", [
    [],
    "this should be an object"
])
def test_create_event_with_invalid_payload(client, events_test_data, invalid_payload):
    payload = {
        "event_type": "order.created",
        "payload": invalid_payload
    }

    headers = {
        "Authorization": f"Bearer {events_test_data['api_key']}"
    }

    response = client.post("/events/", json=payload, headers=headers)

    assert response.status_code == 422

    assert events_collection.count_documents({"client_id": events_test_data["client_id"]}) == 0

    assert deliveries_collection.count_documents({"client_id": events_test_data["client_id"]}) == 0
