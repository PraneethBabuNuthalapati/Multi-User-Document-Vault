from passlib.context import CryptContext
from jose import jwt, JWTError
from datetime import datetime, timedelta
import hashlib
from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
import os
from dotenv import load_dotenv

load_dotenv()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")

pwd_context = CryptContext(
    schemes=["bcrypt"],
    deprecated = "auto"
)

def preprocess_password(password: str):
    return hashlib.sha256(password.encode()).hexdigest()

def hash_password(password:str):
    print("Hash Function Called")
    password = preprocess_password(password)
    print("AFTER SHA256: ", password)
    return pwd_context.hash(password)

def verify_password(plain_password:str, hashed_password:str):
    plain_password = preprocess_password(plain_password)
    return pwd_context.verify(plain_password, hashed_password)

def create_access_token(data: dict):
    to_encode = data.copy()
    
    expire = datetime.utcnow() + timedelta(hours=2)
    to_encode.update({"exp": expire})
    
    encoded_jwt = jwt.encode(
        to_encode,
        SECRET_KEY,
        algorithm=ALGORITHM
    )
    
    return encoded_jwt

# def get_current_user(token: str = Depends(oauth2_scheme)):
#     try:
#         payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
#         user_id = payload.get("user_id")
        
#         if user_id is None:
#             raise HTTPException(status_code=401, detail="Invalid token")
#         return user_id
    
#     except JWTError:
#         raise HTTPException(status_code=401, detail="Invalid token")

#FastAPI's auth system

def get_current_user(token: str = Depends(oauth2_scheme)):
    payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    return payload.get("user_id")