from database import events_collection
from bson import ObjectId

def save_event(client_id, event_type, payload, created_at):
    data = {}
    data["client_id"] = client_id
    data["event_type"] = event_type
    data["payload"] = payload
    data["created_at"] = created_at

    result = events_collection.insert_one(data)
    return result.inserted_id


def get_event_by_id(event_id):
    return events_collection.find_one({"_id": ObjectId(event_id)})