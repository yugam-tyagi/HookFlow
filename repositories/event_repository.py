from database import events_collection

def save_event(client_id, event_type, payload, created_at):
    data = {}
    data["client_id"] = client_id
    data["event_type"] = event_type
    data["payload"] = payload
    data["created_at"] = created_at

    result = events_collection.insert_one(data)
    return result.inserted_id