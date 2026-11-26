from repositories import event_repository, webhook_endpoint_repository, delivery_repository
from schemas.event import EventResponse
from schemas.delivery import DeliveryTrackingResponse
from datetime import datetime, timezone
from tasks import delivery_tasks
from fastapi import status, HTTPException

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


def get_deliveries_by_event(client, event_id):
    client_id = client["_id"]
    deliveries = list(delivery_repository.get_deliveries_by_client_and_event(client_id, event_id))

    if not deliveries:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Incorrect event ID or no deliveries found for the given event ID")

    response = []

    for delivery in deliveries:
        response.append(DeliveryTrackingResponse(
            delivery_id = str(delivery["_id"]),
            endpoint_id = str(delivery["endpoint_id"]),
            status = delivery["status"],
            attempt_count = delivery["attempt_count"],
            http_status = delivery.get("http_status"),
            response_body = delivery.get("response_body"),
            error_message = delivery.get("error_message"),
            next_attempt_at = delivery.get("next_attempt_at"),
            completed_at = delivery.get("completed_at")
        ))

    return response