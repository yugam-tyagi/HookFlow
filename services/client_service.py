from repositories import client_repository
from datetime import datetime, timezone
from schemas.client import ClientResponse

def get_all_clients() -> list[ClientResponse]:
    clients = client_repository.get_all_clients()
    result = []

    for client in clients:
        result.append(ClientResponse(
            id=str(client["_id"]),
            name=client["name"],
            active=client["active"],
            created_at=client["created_at"])
        )

    return result

def create_client(data) -> ClientResponse:
    client = data.copy()
    client["active"] = True
    client["created_at"] = datetime.now(timezone.utc)

    result = client_repository.save_client(client)

    return ClientResponse(
        id=str(result.inserted_id),
        name=client["name"],
        active=client["active"],
        created_at=client["created_at"]
    )