from database import clients_collection

def get_all_clients():
    clients = clients_collection.find()
    return clients

def save_client(data):
    return clients_collection.insert_one(data)