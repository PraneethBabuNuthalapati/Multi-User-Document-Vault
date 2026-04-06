from fastapi import FastAPI
from .database import engine, Base
from .routes import user, documents

app = FastAPI()

Base.metadata.create_all(bind=engine)

app.include_router(user.router)
app.include_router(documents.router)