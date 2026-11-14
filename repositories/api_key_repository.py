from database import api_keys_collection

def save_client_api_key(data):
    api_keys_collection.update_one(
        {"client_id": data["client_id"]},
        {"$set": data},
        upsert=True
    )