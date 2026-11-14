from fastapi import APIRouter,status
from services import client_service
from schemas.client import ClientCreate,ClientResponse

router = APIRouter(prefix="/clients",tags=["clients"])

@router.get("/",response_model=list[ClientResponse])
def get_clients():
    return client_service.get_all_clients()

@router.post("/",response_model=ClientResponse,status_code=status.HTTP_201_CREATED)
def create_client(request: ClientCreate):
    data = request.model_dump()
    return client_service.create_client(data)
