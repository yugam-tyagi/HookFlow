from database import webhook_endpoints_collection
from datetime import datetime, timezone
from bson import ObjectId

def upsert_webhook_endpoint(client_id, url, subscribed_events):    
    result = webhook_endpoints_collection.update_one(
        {"client_id":client_id, "url":url},
        {
            "$setOnInsert": {
                "client_id": client_id,
                "url": url,
                "active": True,
                "created_at": datetime.now(timezone.utc)
            },
            "$addToSet": {
                "subscribed_events": {
                    "$each": subscribed_events
                }
            }
        },
        upsert= True
    )

    is_created = result.upserted_id is not None
    endpoint_data = webhook_endpoints_collection.find_one({"client_id":client_id, "url":url})

    return endpoint_data, is_created


def get_webhook_endpoints_by_client(client_id):
    return webhook_endpoints_collection.find({"client_id": client_id})


def get_webhook_endpoint_by_id(client_id, endpoint_id):
    return webhook_endpoints_collection.find_one({"_id": ObjectId(endpoint_id), "client_id": client_id})


def delete_webhook_endpoint(client_id, endpoint_id):
    return webhook_endpoints_collection.delete_one({"_id": ObjectId(endpoint_id), "client_id": client_id})

def get_active_endpoints_by_event(client_id, event_type):
    return webhook_endpoints_collection.find({"client_id": client_id, "active": True, "subscribed_events":event_type})