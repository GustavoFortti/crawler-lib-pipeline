import base64
import hashlib

def encode_url_base64(string: str) -> str:
    """
    Codifica uma string em base64.
    :param string: A string a ser codificada em base64.
    :return: A string codificada em base64.
    """
    encoded_bytes = base64.b64encode(string.encode("utf-8"))
    encoded_string = encoded_bytes.decode("utf-8")
    return encoded_string

def create_hash_sha256(string: str) -> str:
    """
    Calcula o hash SHA-256 de uma string.
    :param string: A string a ser processada.
    :return: O hash SHA-256 da string.
    """
    bytes_string = string.encode('utf-8')
    sha256_hash = hashlib.sha256(bytes_string).hexdigest()
    return sha256_hash