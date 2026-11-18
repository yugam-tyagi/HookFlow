from database import deliveries_collection

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