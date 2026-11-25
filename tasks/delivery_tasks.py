import httpx, json
from celery_app import celery_app
from repositories import delivery_repository, webhook_endpoint_repository, event_repository
from exceptions import event_exception, webhook_endpoint_exception
from schemas.webhook_event import WebhookEventPayload
from services import retry_service, signature_service
from datetime import datetime, timezone, timedelta

@celery_app.task(name="process_delivery")
def process_delivery(delivery_id: str):
    delivery = delivery_repository.claim_delivery(delivery_id)
    if delivery is None:
        return

    client_id = delivery["client_id"]
    endpoint_id = delivery["endpoint_id"]
    event_id = delivery["event_id"]

    event = event_repository.get_event_by_id(event_id)
    if event is None:
        delivery_repository.mark_delivery_failed(delivery_id,"Event doesn't exist")
        raise event_exception.EventNotFoundException("Event doesn't exist")
    
    endpoint = webhook_endpoint_repository.get_webhook_endpoint_by_id(client_id,endpoint_id)
    if endpoint is None:
        delivery_repository.mark_delivery_failed(delivery_id,"Endpoint doesn't exist")
        raise webhook_endpoint_exception.WebhookEndpointNotFoundException("Endpoint doesn't exist")

    event_payload = WebhookEventPayload(
        id = str(event_id),
        type = event["event_type"],
        created_at = event["created_at"],
        data = event["payload"]
    )

    payload = event_payload.model_dump(mode='json')
    signing_secret = endpoint["signing_secret"]
    serialized_payload = json.dumps(payload,separators=(",",":")).encode("utf-8")
    timestamp = datetime.now(timezone.utc)
    unix_timestamp = str(int(timestamp.timestamp()))

    signature = signature_service.generate_signature(signing_secret,serialized_payload,unix_timestamp)

    headers = {
        "Content-Type": "application/json",
        "X-HookFlow-Timestamp": unix_timestamp,
        "X-HookFlow-Signature": signature,
    }

    with httpx.Client(timeout=10.0) as client:
        response_status = 0
        response_body = None
        error_message = None
        try:
            delivery_repository.increment_attempt_count(delivery_id)
            response = client.post(endpoint["url"],headers=headers,content=serialized_payload)
            response_status = response.status_code
            response_body = response.text[:4096]
        except httpx.TimeoutException as e:
            error_message = str(e)
        except httpx.ConnectError as e:
            error_message = str(e)
        except httpx.RequestError as e:
            error_message = str(e)

    current_attempt_count = delivery_repository.get_attempt_count(delivery_id)
    delivery_status = retry_service.should_retry(current_attempt_count, response_status)

    if delivery_status == "delivered" or delivery_status == "failed":
        completed_at = datetime.now(timezone.utc)
        delivery_repository.update_delivery_outcome(delivery_id,delivery_status,response_status,response_body,error_message,completed_at)
    else:
        delay = retry_service.calculate_retry_delay(current_attempt_count)
        next_attempt_at = datetime.now(timezone.utc) + timedelta(seconds=delay)
        delivery_repository.schedule_delivery_retry(delivery_id,response_status,response_body,error_message,next_attempt_at)
        process_delivery.apply_async(args=[delivery_id],countdown=delay)