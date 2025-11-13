from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt_sha256"], deprecated="auto") #tells passlib to use bcrypt hashing algorithm

def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(user_input_password: str, db_password: str) -> bool: #since passwords in db are hashed, we need to hash the plain password and compare
    return pwd_context.verify(user_input_password, db_password) #verify does the hashing and comparison