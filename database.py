from pymongo import MongoClient

MONGO_URL = "mongodb://localhost:27017"

client = MongoClient(MONGO_URL)

# Verify MongoDB connection
try:
    client.admin.command("ping")
    print("Connected to MongoDB successfully!")
except Exception as e:
    print(f"MongoDB connection failed: {e}")

# Select our database
db = client["hookflow"]

# Select collections
clients_collection = db["clients"]
api_keys_collection = db["api_keys"]
