import base64
import hashlib

def encode_url_base64(string: str) -> str:
    encoded_bytes = base64.b64encode(string.encode("utf-8"))
    encoded_string = encoded_bytes.decode("utf-8")
    return encoded_string

def create_hash_sha256(string: str) -> str:
    bytes_string = string.encode('utf-8')
    sha256_hash = hashlib.sha256(bytes_string).hexdigest()
    return sha256_hash