from database import deliveries_collection
from bson import ObjectId
from datetime import datetime, timezone, timedelta
from pymongo import ReturnDocument

def create_deliveries(event_id, client_id, endpoints, timestamp):
    deliveries =[]

    for endpoint in endpoints:
        endpoint_id = endpoint["_id"]
        deliveries.append({
            "event_id": event_id,
            "client_id": client_id,
            "endpoint_id": endpoint_id,
            "status": "pending",
            "attempt_count": 0,
            "next_attempt_at": timestamp,
            "created_at": timestamp
        })

    if not deliveries:
        return deliveries

    result = deliveries_collection.insert_many(deliveries)

    return result.inserted_ids


def get_delivery_by_id(delivery_id):
    return deliveries_collection.find_one({"_id": ObjectId(delivery_id)})


def update_delivery_outcome(delivery_id, status, http_status, response_body, error_message, completed_at):
    deliveries_collection.update_one(
        {"_id": ObjectId(delivery_id)},
        {
            "$set": {
                "status": status,
                "http_status": http_status,
                "response_body": response_body,
                "error_message": error_message,
                "completed_at": completed_at
            },
            "$unset": {
                "next_attempt_at": "",
                "processing_started_at": "",
                "lease_expires_at": ""
            }
        }
    )


def schedule_delivery_retry(delivery_id, http_status, response_body, error_message, next_attempt_at):
    deliveries_collection.update_one(
        {"_id": ObjectId(delivery_id)},
        {
            "$set": {
                "status": "retrying",
                "http_status": http_status,
                "response_body": response_body,
                "error_message": error_message,
                "next_attempt_at": next_attempt_at
            },
            "$unset": {
                "processing_started_at": "",
                "lease_expires_at": ""
            }
        }
    )


def claim_delivery(delivery_id):
    now = datetime.now(timezone.utc)

    claimed_delivery = deliveries_collection.find_one_and_update(
        {
            "_id": ObjectId(delivery_id),
            "$or": [
                {
                    "status": "pending",
                    "next_attempt_at": {"$lte": now}
                },
                {
                    "status": "retrying",
                    "next_attempt_at": {"$lte": now}
                },
                {
                    "status": "processing",
                    "lease_expires_at": {"$lte": now}
                }
            ]
        },
        {
            "$set": {
                "processing_started_at": now,
                "status": "processing",
                "lease_expires_at": now + timedelta(seconds=60)
            }
        },
        return_document=ReturnDocument.AFTER  
    )

    if claimed_delivery is None:
        return None
    return claimed_delivery


def get_deliveries_for_recovery(current_timestamp):
    cursor = deliveries_collection.find(
        {
            "$or": [
                {
                    "status": "pending",
                    "next_attempt_at": {"$lte": current_timestamp}
                },
                {
                    "status": "retrying",
                    "next_attempt_at": {"$lte": current_timestamp}
                },
                {
                    "status": "processing",
                    "lease_expires_at": {"$lte": current_timestamp}
                }
            ]
        }
    ).sort("next_attempt_at",1).limit(100)

    delivery_ids=[]
    for item in cursor:
        delivery_ids.append(item["_id"])

    return delivery_ids

def mark_delivery_failed(delivery_id, error_message):
    completed_at = datetime.now(timezone.utc)

    deliveries_collection.update_one(
        {"_id": ObjectId(delivery_id)},
        {
            "$set": {
                "status": "failed",
                "error_message": error_message,
                "completed_at": completed_at
            },
            "$unset": {
                "next_attempt_at": "",
                "lease_expires_at": ""
            }
        }
    )


def increment_attempt_count(delivery_id):
    deliveries_collection.update_one(
        {"_id": ObjectId(delivery_id)},
        {
            "$inc": {
                "attempt_count": 1
            }
        }
    )


def get_attempt_count(delivery_id):
    delivery = deliveries_collection.find_one({"_id": ObjectId(delivery_id)})
    return delivery["attempt_count"]