import hashlib
import os


def generate_salt_bytes(length: int = 16) -> bytes:
    return os.urandom(length)

def hash_otp(otp_code: str, salt: bytes) -> str:
    otp_bytes = otp_code.encode('utf-8')
    salted_otp = salt + otp_bytes
    hashed_object = hashlib.sha256(salted_otp)
    return hashed_object.hexdigest()