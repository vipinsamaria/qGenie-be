from auth.jwt_utils import get_current_user
from fastapi import APIRouter, Depends, HTTPException, Request, Query
from sqlalchemy.orm import Session
from db.database import get_db_session
from db.models import KnowledgeBase

router = APIRouter(prefix="/api/educator", tags=["Educator"])

@router.get("/knowledge_base")
async def get_knowledge_base_items(
    request: Request,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db_session),
    limit: int = 10,
    offset: int = 0
):
    if current_user["type"] != "educator":
        raise HTTPException(status_code=403, detail="Only educators can access knowledge base")

    query = db.query(KnowledgeBase).filter(KnowledgeBase.inserted_by == current_user["sub"])
    total = query.count()
    items = query.offset(offset).limit(limit).all()
    result = [
        {
            "id": str(item.id),
            "curriculum": item.curriculum,
            "standard": item.standard,
            "subject": item.subject,
            "chapter": item.chapter,
            "file_url": item.file_url
        }
        for item in items
    ]
    return {
        "knowledge_base": result,
        "total": total,
        "limit": limit,
        "offset": offset
    } 