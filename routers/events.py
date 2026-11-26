from bson import ObjectId
from fastapi import APIRouter, Depends, status, HTTPException
from schemas.event import EventCreate, EventResponse
from schemas.delivery import DeliveryTrackingResponse
from dependencies.auth import get_authenticated_client 
from services import event_service

router = APIRouter(prefix="/events", tags=["events"])

@router.post("/", response_model=EventResponse, status_code=status.HTTP_202_ACCEPTED)
def create_event(request: EventCreate, client=Depends(get_authenticated_client)):
    event_data = request.model_dump()
    response = event_service.create_event(client, event_data)
    return response


@router.get("/{event_id}/deliveries", response_model=list[DeliveryTrackingResponse], status_code=status.HTTP_200_OK)
def get_deliveries_by_event(event_id: str, client=Depends(get_authenticated_client)):
    if not ObjectId.is_valid(event_id):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid event ID format")
    
    return event_service.get_deliveries_by_event(client, event_id)