from fastapi import HTTPException, status, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from services import api_key_service
from exceptions.client_exception import ClientNotFoundException, InactiveClientException
from exceptions.api_key_exception import InactiveApiKeyException, InvalidApiKeyException

security = HTTPBearer()

def get_authenticated_client(credentials: HTTPAuthorizationCredentials = Depends(security)):
    api_key = credentials.credentials

    try:
        return api_key_service.authenticate_api_key(api_key)
    
    except (InvalidApiKeyException, InactiveApiKeyException, InactiveClientException, ClientNotFoundException):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or inactive API key"
        )