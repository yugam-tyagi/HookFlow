from datetime import datetime, timezone
from fastapi import FastAPI, status
from database import clients_collection
from schemas.client import ClientCreate

app = FastAPI(
    title="HookFlow",
    description="Reliable Webhook Delivery Platform",
    version="1.0.0"
)

@app.get("/health")
def health_check():
    return {
        "status": "UP",
        "service": "HookFlow"
    }


@app.get("/clients")
def get_clients():
    clients = clients_collection.find()

    result = []

    for client in clients:
        result.append({
            "id": str(client["_id"]),
            "name": client["name"],
            "active": client["active"],
            "created_at": client["created_at"].isoformat()
        })

    return result

@app.post("/clients",status_code=status.HTTP_201_CREATED)
def create_client(request: ClientCreate):

    data = request.model_dump()
    data["active"] = True
    data["created_at"] = datetime.now(timezone.utc)

    result = clients_collection.insert_one(data)

    return {
        "id": str(result.inserted_id),
        "name": data["name"],
        "active": data["active"],
        "created_at": data["created_at"].isoformat()
    }