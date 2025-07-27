from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from uuid import UUID

from db.database import get_db, get_db_session
from db.models import Institution, Curriculum, Standard, Subject, Topic
from auth.jwt_utils import get_current_user
from .schemas import (
    CurriculumResponse,
    StandardsListResponse,
    SubjectsListResponse,
    TopicsListResponse,
    CurriculumsListResponse
)

router = APIRouter(
    prefix="/paper-props",
    tags=["paper-props"]
)

@router.get("/curriculums", response_model=CurriculumsListResponse)
async def get_all_curriculums(
    db: Session = Depends(get_db_session)
):
    """Fetch all available curriculums"""
    curriculums = db.query(Curriculum).all()
    
    if not curriculums:
        raise HTTPException(status_code=404, detail="No curriculums found")

    return CurriculumsListResponse(
        curriculums=[
            CurriculumResponse(
                id=curriculum.id,
                name=curriculum.curriculum
            )
            for curriculum in curriculums
        ]
    )

@router.get("/curriculum/{educator_id}", response_model=CurriculumResponse)
async def get_educator_curriculum(
    educator_id: UUID,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db_session)
):
    """Fetch curriculum for the educator based on their institution affiliation"""
    # Get educator's institution and associated curriculum
    institution = db.query(Institution)\
        .join(Institution.educators)\
        .filter(Institution.educators.any(id=educator_id))\
        .first()
    
    if not institution:
        raise HTTPException(status_code=404, detail="Educator's institution not found")

    curriculum = db.query(Curriculum)\
        .filter(Curriculum.id == institution.curriculum_id)\
        .first()
    
    if not curriculum:
        raise HTTPException(status_code=404, detail="Curriculum not found")

    return CurriculumResponse(
        id=curriculum.curriculum,
        name=curriculum.curriculum
    )

@router.get("/standards/{curriculum_id}", response_model=StandardsListResponse)
async def get_curriculum_standards(
    curriculum_id: UUID,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db_session)
):
    """Fetch all standards for a given curriculum"""
    standards = db.query(Standard)\
        .filter(Standard.curriculum_id == curriculum_id)\
        .all()
    
    if not standards:
        raise HTTPException(status_code=404, detail="No standards found for this curriculum")

    return StandardsListResponse(
        standards=[
            {
                "id": standard.id,
                "name": standard.standard
            }
            for standard in standards
        ]
    )

@router.get("/subjects/{standard_id}", response_model=SubjectsListResponse)
async def get_standard_subjects(
    standard_id: UUID,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db_session)
):
    """Fetch all subjects for a given standard"""
    subjects = db.query(Subject)\
        .filter(Subject.standard_id == standard_id)\
        .all()
    
    if not subjects:
        raise HTTPException(status_code=404, detail="No subjects found for this standard")

    return SubjectsListResponse(
        subjects=[
            {
                "id": subject.id,
                "name": subject.subject
            }
            for subject in subjects
        ]
    )

@router.get("/topics/{subject_id}", response_model=TopicsListResponse)
async def get_subject_topics(
    subject_id: UUID,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Fetch all topics for a given subject"""
    topics = db.query(Topic)\
        .filter(Topic.subject_id == subject_id)\
        .all()
    
    if not topics:
        raise HTTPException(status_code=404, detail="No topics found for this subject")

    return TopicsListResponse(
        topics=[
            {
                "topic_id": topic.id,
                "topic": topic.topic
            }
            for topic in topics
        ]
    ) 