from repositories import client_repository, api_key_repository
from utils import api_key_utils
from datetime import datetime, timezone
from bson.errors import InvalidId
from exceptions.client_exception import InvalidClientIdException, InactiveClientException, ClientNotFoundException
from exceptions.api_key_exception import InactiveApiKeyException, InvalidApiKeyException

def generate_api_key_for_client(client_id):
    try:
        client = client_repository.get_client_by_id(client_id)
    except InvalidId:
        raise InvalidClientIdException("Invalid client ID")

    if client is None:
        raise ClientNotFoundException("Client doesn't exist") 
    
    if not client["active"]:
        raise InactiveClientException("Client is inactive")

    api_key = api_key_utils.generate_api_key()
    api_key_hash = api_key_utils.hash_api_key(api_key)

    data = {}
    data["client_id"] = client["_id"]
    data["name"] = client["name"]
    data["key_hash"] = api_key_hash
    data["active"] = True
    data["created_at"] = datetime.now(timezone.utc)

    api_key_repository.save_client_api_key(data)

    return api_key


def authenticate_api_key(api_key: str):
    key_hash = api_key_utils.hash_api_key(api_key)

    api_key_doc = api_key_repository.get_api_key_by_hash(key_hash)

    if api_key_doc is None:
        raise InvalidApiKeyException("Api key is invalid")
    
    if not api_key_doc["active"]:
        raise InactiveApiKeyException("Api key is inactive")

    client = client_repository.get_client_by_id(api_key_doc["client_id"])

    if client is None:
        raise ClientNotFoundException("Client doesn't exist")

    if not client["active"]:
        raise InactiveClientException("Client is inactive")
    
    return client