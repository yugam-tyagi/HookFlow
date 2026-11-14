import secrets
import hashlib

def generate_api_key():
    token = secrets.token_urlsafe(32)
    key = f"hf_live_{token}"
    return key

def hash_api_key(api_key:str) -> str:
    return hashlib.sha256(api_key.encode()).hexdigest()