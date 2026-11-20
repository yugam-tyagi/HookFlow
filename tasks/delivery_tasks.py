import httpx
from celery_app import celery_app
from repositories import delivery_repository, webhook_endpoint_repository, event_repository
from exceptions import delivery_exception, event_exception, webhook_endpoint_exception
from schemas.webhook_event import WebhookEventPayload
from datetime import datetime, timezone

@celery_app.task(name="process_delivery")
def process_delivery(delivery_id: str):
    delivery = delivery_repository.get_delivery_by_id(delivery_id)
    if delivery is None:
        raise delivery_exception.DeliveryNotFoundException("Delivery doesn't exist")

    client_id = delivery["client_id"]
    endpoint_id = delivery["endpoint_id"]
    event_id = delivery["event_id"]
    event = event_repository.get_event_by_id(event_id)
    if event is None:
        raise event_exception.EventNotFoundException("Event doesn't exist")
    
    endpoint = webhook_endpoint_repository.get_webhook_endpoint_by_id(client_id,endpoint_id)
    if endpoint is None:
        raise webhook_endpoint_exception.WebhookEndpointNotFoundException("Endpoint doesn't exist")

    event_payload = WebhookEventPayload(
        id = str(event_id),
        type = event["event_type"],
        created_at = event["created_at"],
        data = event["payload"]
    )

    payload = event_payload.model_dump(mode='json')

    with httpx.Client(timeout=10.0) as client:
        response_status = None
        response_body = None
        error_message = None
        is_success = False
        try:
            delivery_repository.increment_attempt_count(delivery_id)
            response = client.post(endpoint["url"],json=payload)
            response_status = response.status_code
            response_body = response.text[:4096]
            if response.is_success:
                is_success = True
        except httpx.TimeoutException as e:
            error_message = str(e)
        except httpx.ConnectError as e:
            error_message = str(e)
        except httpx.RequestError as e:
            error_message = str(e)

    status = "delivered"
    completed_at = datetime.now(timezone.utc)
    if not is_success: 
        status = "failed"

    delivery_repository.update_delivery_outcome(delivery_id,status,response_status,response_body,error_message,completed_at)