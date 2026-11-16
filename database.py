
from pymongo import MongoClient

MONGO_URL = "mongodb://localhost:27017"

client = MongoClient(MONGO_URL, tz_aware=True)

db = client["hookflow"]

clients_collection = db["clients"]
api_keys_collection = db["api_keys"]
webhook_endpoints_collection = db["webhook_endpoints"]

def check_database_connection():
    client.admin.command("ping")
    print("Connected to MongoDB successfully!")
