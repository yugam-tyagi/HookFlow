from repositories import webhook_endpoint_repository
from schemas.webhook_endpoint import WebhookEndpointResponse
from exceptions.webhook_endpoint_exception import WebhookEndpointNotFoundException
from bson.errors import InvalidId

def register_webhook_endpoint(client, data):
    client_id = client["_id"]
    url = str(data["url"])
    subscribed_events = data["subscribed_events"]

    endpoint_data, is_created = webhook_endpoint_repository.upsert_webhook_endpoint(client_id, url, subscribed_events)

    response = WebhookEndpointResponse(
        id = str(endpoint_data["_id"]),
        url = endpoint_data["url"],
        subscribed_events = endpoint_data["subscribed_events"],
        active = endpoint_data["active"],
        created_at = endpoint_data["created_at"]
    )

    return response, is_created


def get_webhook_endpoints(client):
    client_id = client["_id"]
    endpoint_data = webhook_endpoint_repository.get_webhook_endpoints_by_client(client_id)

    response = []

    for doc in endpoint_data:
        response.append(WebhookEndpointResponse(
        id = str(doc["_id"]),
        url = doc["url"],
        subscribed_events = doc["subscribed_events"],
        active = doc["active"],
        created_at = doc["created_at"]
    ))
        
    return response


def get_webhook_endpoint(client, endpoint_id):
    client_id = client["_id"]

    try:
        endpoint_data = webhook_endpoint_repository.get_webhook_endpoint_by_id(client_id, endpoint_id)
    except InvalidId:
        raise WebhookEndpointNotFoundException("Webhook endpoint doesn't exist")

    if endpoint_data is None:
        raise WebhookEndpointNotFoundException("Webhook endpoint doesn't exist")
    
    response = WebhookEndpointResponse(
            id = str(endpoint_data["_id"]),
            url = endpoint_data["url"],
            subscribed_events = endpoint_data["subscribed_events"],
            active = endpoint_data["active"],
            created_at = endpoint_data["created_at"]
        )
    
    return response


def delete_webhook_endpoint(client, endpoint_id):
    client_id = client["_id"]

    try:
        deleted_count = webhook_endpoint_repository.delete_webhook_endpoint(client_id, endpoint_id)
    except InvalidId:
        raise WebhookEndpointNotFoundException("Webhook endpoint doesn't exist")

    if deleted_count == 0:
        raise WebhookEndpointNotFoundException("Webhook endpoint doesn't exist")
    
    return deleted_count