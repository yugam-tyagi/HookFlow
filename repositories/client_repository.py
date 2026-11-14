from database import clients_collection
from bson import ObjectId

def get_all_clients():
    return clients_collection.find()

def save_client(data):
    return clients_collection.insert_one(data)

def get_client_by_id(client_id):
    object_id = ObjectId(client_id)
    return clients_collection.find_one({"_id":object_id})