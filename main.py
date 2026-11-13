from fastapi import FastAPI
from database import clients_collection

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
