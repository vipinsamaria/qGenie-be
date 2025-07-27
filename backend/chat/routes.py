from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from db.database import get_db_session
from pydantic import BaseModel
from auth.jwt_utils import get_current_user
from chat.utils import get_bot_reponse

router = APIRouter(prefix="/chat", tags=["Chat"])

class SubmitResponse(BaseModel):
    success: bool
    bot: dict
    type: str

class SubmitMessageRequest(BaseModel):
    curriculum: dict
    standard: dict
    subject: dict
    topics: list[dict]
    question_config: list[dict]
    query: str

@router.post("/submit", response_model=SubmitResponse)
async def submit_message(
    payload: SubmitMessageRequest,
    db: Session = Depends(get_db_session),
    current_user: dict = Depends(get_current_user)
):
    """Handle user message and create next chat based on the flow."""
    # Verify user is an educator
    if current_user["type"] != "educator":
        raise HTTPException(status_code=403, detail="Only educators can access chat")
    
    educator_id = current_user["sub"]
    req_body = {
        "educator_id": educator_id,
        "curriculum": payload.curriculum,
        "standard": payload.standard,
        "subject": payload.subject,
        "topics": payload.topics, 
        "question_config": payload.question_config,
        "user": educator_id,
        "query": payload.query
    }
    
    new_bot_message = get_bot_reponse(req_body)
    print(new_bot_message)
    return SubmitResponse(
        success=True,
        bot=new_bot_message["bot"] or {},
        type=new_bot_message["type"] or ''
    )