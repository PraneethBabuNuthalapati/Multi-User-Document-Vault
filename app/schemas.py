from pydantic import BaseModel, EmailStr

class UserCreate(BaseModel):
    email: EmailStr
    password: str
    
class UserLogin(BaseModel):
    email: EmailStr
    password: str
    
class FileResponse(BaseModel):
    id: int
    filename: str
    filepath: str
    
    class Config:
        from_attributes = True