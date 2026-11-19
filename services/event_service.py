from repositories import event_repository, webhook_endpoint_repository, delivery_repository
from schemas.event import EventResponse
from datetime import datetime, timezone
from tasks import delivery_tasks

def create_event(client, event_data):
    client_id = client["_id"]
    event_type = event_data["event_type"]
    payload = event_data["payload"]
    created_at = datetime.now(timezone.utc)

    event_id = event_repository.save_event(client_id, event_type, payload, created_at)

    endpoints = webhook_endpoint_repository.get_active_endpoints_by_event(client_id, event_type)

    delivery_ids = delivery_repository.create_deliveries(event_id, client_id, endpoints, created_at)

    for delivery_id in delivery_ids:
        delivery_tasks.process_delivery.delay(str(delivery_id))

    return EventResponse(
        id = str(event_id),
        event_type = event_type,
        created_at = created_at
    )