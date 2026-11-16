from fastapi import APIRouter, status, Depends, Response, HTTPException
from schemas.webhook_endpoint import WebhookEndpointCreate, WebhookEndpointResponse
from services import webhook_endpoint_service
from dependencies.auth import get_authenticated_client
from exceptions.webhook_endpoint_exception import WebhookEndpointNotFoundException

router = APIRouter(prefix="/webhook-endpoints", tags=["webhook_endpoints"])

@router.post("/",response_model=WebhookEndpointResponse)
def register_webhook_endpoint(request: WebhookEndpointCreate, response: Response, client=Depends(get_authenticated_client)):
    data = request.model_dump()
    endpoint_response, is_created = webhook_endpoint_service.register_webhook_endpoint(client,data)

    response.status_code = status.HTTP_200_OK

    if is_created:
        response.status_code = status.HTTP_201_CREATED

    return endpoint_response


@router.get("/",response_model=list[WebhookEndpointResponse],status_code=status.HTTP_200_OK)
def get_webhook_endpoints(client=Depends(get_authenticated_client)):
    return webhook_endpoint_service.get_webhook_endpoints(client)


@router.get("/{endpoint_id}",status_code=status.HTTP_200_OK,response_model=WebhookEndpointResponse)
def get_webhook_endpoint(endpoint_id:str, client=Depends(get_authenticated_client)):
    try:
        return webhook_endpoint_service.get_webhook_endpoint(client, endpoint_id)
    except WebhookEndpointNotFoundException as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    

@router.delete("/{endpoint_id}",status_code=status.HTTP_204_NO_CONTENT)
def delete_webhook_endpoint(endpoint_id: str, client=Depends(get_authenticated_client)):
    try: 
        webhook_endpoint_service.delete_webhook_endpoint(client, endpoint_id)
    except WebhookEndpointNotFoundException as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))