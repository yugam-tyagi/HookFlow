import hmac
import hashlib

def generate_signature(signing_secret:str,body:bytes,timestamp:str) -> str:
    message = timestamp.encode("utf-8") + b"." + body
    signature = hmac.new(key=signing_secret.encode("utf-8"),msg=message,digestmod=hashlib.sha256).hexdigest()
    return signature