from fastapi import APIRouter, Depends, status
from schemas.event import EventCreate, EventResponse
from dependencies.auth import get_authenticated_client 
from services import event_service

router = APIRouter(prefix="/events", tags=["events"])

@router.post("/", response_model=EventResponse, status_code=status.HTTP_202_ACCEPTED)
def create_event(request: EventCreate, client=Depends(get_authenticated_client)):
    event_data = request.model_dump()
    response = event_service.create_event(client, event_data)
    return response