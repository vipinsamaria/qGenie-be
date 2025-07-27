from fastapi import APIRouter, Depends, HTTPException, File, UploadFile
from sqlalchemy.orm import Session
from typing import List
from uuid import UUID

from db.database import get_db, get_db_session
from db.models import Institution, Curriculum, Standard, Subject, Topic, KnowledgeBase
from auth.jwt_utils import get_current_user
from .schemas import (
    CurriculumResponse,
    StandardsListResponse,
    SubjectsListResponse,
    TopicsListResponse,
    CurriculumsListResponse,
    AddKnowledgeBaseRequest,
    AddKnowledgeBaseResponse
)
import datetime
from google.cloud import storage
import os

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

@router.post("/add_kb", response_model=AddKnowledgeBaseResponse)
async def add_knowledge_base(
    curriculum: str,
    standard: str,
    subject: str,
    title: str,
    file: UploadFile = File(...),
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db_session)
):
    """Add a new knowledge base entry with file upload."""
    try:
        # Verify user is an educator
        if current_user["type"] != "educator":
            raise HTTPException(status_code=403, detail="Only educators can add knowledge base items")

        # Save file to temporary location
        temp_file_path = f"/tmp/{file.filename}"
        with open(temp_file_path, "wb+") as file_object:
            file_object.write(await file.read())

        # Upload to Google Cloud Storage
        project_id = "qgenie-467111"  # Replace with your project ID
        bucket_name = "qgenie-question-papers"  # Replace with your bucket name
        unique_id = os.urandom(6).hex()
        destination_blob_name = f"kb/{unique_id}_{file.filename}"

        storage_client = storage.Client(project=project_id)
        bucket = storage_client.bucket(bucket_name)
        blob = bucket.blob(destination_blob_name)
        
        # Upload the file
        blob.upload_from_filename(temp_file_path)
        
        # Generate a signed URL that doesn't expire
        file_url = f"gs://{bucket_name}/{destination_blob_name}"

        # Clean up temporary file
        os.remove(temp_file_path)

        # Create knowledge base entry
        kb_entry = KnowledgeBase(
            curriculum=curriculum,
            standard=standard,
            subject=subject,
            chapter=title,  # Using title as chapter
            file_url=file_url,
            inserted_by=current_user["sub"]
        )
        
        db.add(kb_entry)
        db.commit()

        return AddKnowledgeBaseResponse(
            success=True,
            message="Knowledge base entry added successfully"
        )

    except Exception as e:
        # Clean up temporary file if it exists
        if os.path.exists(temp_file_path):
            os.remove(temp_file_path)
        
        return AddKnowledgeBaseResponse(
            success=False,
            message=f"Failed to add knowledge base entry: {str(e)}"
        ) 