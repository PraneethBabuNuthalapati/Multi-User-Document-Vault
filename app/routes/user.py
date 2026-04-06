from fastapi import APIRouter, Depends, HTTPException, Header
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from .. import models, schemas,database, auth

router = APIRouter()

def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()
        
@router.post("/signup")
def signup(user: schemas.UserCreate, db:Session = Depends(get_db)):
    existing_user = db.query(models.User).filter(models.User.email == user.email).first()
    
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    hashed_password = auth.hash_password(user.password)
    
    new_user = models.User(
        email = user.email,
        password = hashed_password
    )
    
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    return {"message": "User Created Successfully"}

# @router.post("/login")
# def login(user: schemas.UserLogin, db: Session = Depends(get_db)):
#     db_user = db.query(models.User).filter(
#         models.User.email == user.email
#     ).first()
    
#     if not db_user:
#         raise HTTPException(
#             status_code=400,
#             detail= "Invalid email or password"
#         )
        
#     if not auth.verify_password(user.password, db_user.password):
#         raise HTTPException(
#             status_code=400,
#             detail = "Invalid email or password"
#         )
        
#     token = auth.create_access_token(
#         {"user_id": db_user.id}
#     )
    
#     return {
#         "access_token": token,
#         "token_type": "bearer"
#     }
@router.post("/login")
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    db_user = db.query(models.User).filter(
        models.User.email == form_data.username
    ).first()
    
    if not db_user or not auth.verify_password(form_data.password, db_user.password):
        raise HTTPException(status_code=400, detail = "Invalid Credentials")
    
    token = auth.create_access_token({"user_id": db_user.id})
    
    return {
        "access_token": token,
        "token_type": "bearer"
    }
    
    
@router.get("/profile")
# def get_profile(authorization: str = Header(..., alias="Authorization")):
#     token = authorization.split(" ")[1]
#     user_id = auth.get_current_user(token)
    
#     return {
#         "message": "You are Authenticated",
#         "user_id": user_id
#     }
def get_profile(user_id: int = Depends(auth.get_current_user)):
    return {
        "message": "You are Authenticated",
        "user_id": user_id
    }