from fastapi import APIRouter,status,HTTPException
from services import api_key_service
from exceptions.client_exception import InvalidClientIdException, InactiveClientException, ClientNotFoundException
from schemas.api_key import ApiKeyResponse

router = APIRouter(prefix="/clients",tags=["api_keys"])

@router.post("/{client_id}/api-key",status_code=status.HTTP_201_CREATED,response_model=ApiKeyResponse)
def get_api_key(client_id: str):
    try:
        api_key = api_key_service.generate_api_key_for_client(client_id)
        return {"api_key": api_key}
    
    except InvalidClientIdException as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    
    except ClientNotFoundException as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    
    except InactiveClientException as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))