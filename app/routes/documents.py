from fastapi import APIRouter, UploadFile, File, Depends, HTTPException
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from sqlalchemy import desc, asc
import shutil
import os
import uuid

from .. import models, auth, database

router = APIRouter(prefix="/documents", tags=["Documents"])

def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()
        
#Upload a file
@router.post("/upload")
def upload_file(
    file: UploadFile = File(...),
    user_id: int = Depends(auth.get_current_user),
    db: Session = Depends(get_db)
):
    os.makedirs("uploads", exist_ok=True)
    
    unique_name = f"{uuid.uuid4()}_{file.filename}"
    file_path = f"uploads/{unique_name}"
    
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
        
    new_doc = models.Document(
        filename = file.filename,
        filepath = file_path,
        user_id = user_id
    )
    
    db.add(new_doc)
    db.commit()
    
    return {"message": "File uploaded successfully"}

#View Specific User's Documents
@router.get("/my-documents")
def get_my_documents(
    skip: int = 0,
    limit: int = 10,
    query: str = "",
    user_id: int = Depends(auth.get_current_user),
    db: Session = Depends(get_db),
    sort_by: str = "created_at",
    order: str = "desc"
):
    #Base Query
    docs_query = db.query(models.Document).filter(
        models.Document.user_id == user_id
    )
    
    #Search Functionality
    if query:
        docs_query = docs_query.filter(
            models.Document.filename.ilike(f"%{query}%")
        )
        
    if hasattr(models.Document, sort_by):
        column = getattr(models.Document, sort_by)
        
        if order == "desc":
            docs_query = docs_query.order_by(desc(column))
        else:
            docs_query = docs_query.order_by(asc(column))
    #Total Document Count
    total_documents = docs_query.count()
    
    #Pagination
    docs = docs_query.offset(skip).limit(limit).all()
    
    return{
        "total": total_documents,
        "skip": skip,
        "limit": limit,
        "documents": [
            {
                "id": doc.id,
                "filename": doc.filename,
                "filepath": doc.filepath,
                "user_id": user_id
                
            }
            for doc in docs
        ]
    }

#Delete a File
@router.delete("/delete/{doc_id}")
def delete_document(
    doc_id: int,
    user_id: int = Depends(auth.get_current_user),
    db: Session = Depends(get_db)
):
    doc = db.query(models.Document).filter(
        models.Document.id == doc_id
    ).first()
    
    if not doc:
        raise HTTPException(status_code=404, detail="Document not Found")
    
    if doc.user_id != user_id:
        raise HTTPException(status_code=403, detail="Not Authorized")
    
    #Delete the file from the disk
    if os.path.exists(doc.filepath):
        os.remove(doc.filepath)
        
    #Delete the file from the database
    db.delete(doc)
    db.commit()
    
    return {"message": "Document deleted successfully"}

#Download Files
@router.get("/download/{doc_id}")
def download_document(
    doc_id: int,
    user_id: int = Depends(auth.get_current_user),
    db: Session = Depends(get_db)
):
    doc = db.query(models.Document).filter(
        models.Document.id == doc_id
    ).first()
    
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
    
    if doc.user_id != user_id:
        raise HTTPException(status_code=403, detail= "Not Authorized")
    
    if not os.path.exists(doc.filepath):
        raise HTTPException(status_code=404, detail="File not Found in the disk")
    
    return FileResponse(
        path=doc.filepath,
        filename=doc.filename,
        media_type='application/octet-stream'
    )