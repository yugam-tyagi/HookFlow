from database import deliveries_collection
from bson import ObjectId

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