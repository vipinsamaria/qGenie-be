from pydantic import BaseModel, UUID4
from typing import List

class CurriculumResponse(BaseModel):
    id: str
    name: str

class StandardResponse(BaseModel):
    id: UUID4
    name: str

class SubjectResponse(BaseModel):
    subject_id: UUID4
    subject: str

class TopicResponse(BaseModel):
    topic_id: UUID4
    topic: str

class StandardsListResponse(BaseModel):
    standards: List[StandardResponse]

class SubjectsListResponse(BaseModel):
    subjects: List[SubjectResponse]

class TopicsListResponse(BaseModel):
    topics: List[TopicResponse]

class CurriculumsListResponse(BaseModel):
    curriculums: List[CurriculumResponse] 