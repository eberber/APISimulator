from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt_sha256"], deprecated="auto") #tells passlib to use bcrypt hashing algorithm

def hash_password(password: str) -> str:
    return pwd_context.hash(password)