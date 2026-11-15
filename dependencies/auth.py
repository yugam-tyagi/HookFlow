from fastapi import Header, HTTPException, status
from services import api_key_service
from exceptions.client_exception import ClientNotFoundException, InactiveClientException
from exceptions.api_key_exception import InactiveApiKeyException, InvalidApiKeyException

def get_authenticated_client(authorization: str=Header(default=None)):
    if authorization is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Missing authorization header")
    
    if not authorization.startswith("Bearer "):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid authorization header")

    api_key = authorization.removeprefix("Bearer ")

    try:
        return api_key_service.authenticate_api_key(api_key)
    
    except (InvalidApiKeyException, InactiveApiKeyException, InactiveClientException, ClientNotFoundException):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or inactive API key"
        )