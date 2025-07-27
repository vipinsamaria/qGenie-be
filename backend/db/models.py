from sqlalchemy import Column, String, Integer, Boolean, DateTime, JSON, ForeignKey, ARRAY, UUID, Table, UniqueConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid
from .database import Base

class Institution(Base):
    __tablename__ = "institutions"

    id = Column(UUID, primary_key=True, default=uuid.uuid4)
    type = Column(String, nullable=False)  # institute or school
    affiliation_code = Column(String, unique=True, nullable=False)
    email = Column(String, unique=True, nullable=False)
    name = Column(String, nullable=False)
    district = Column(String)
    state = Column(String)
    country = Column(String)
    educators_count = Column(Integer, default=0)
    quota_remaining = Column(Integer, default=0)
    curriculum_id = Column(UUID, ForeignKey("curriculums.id"), nullable=False)

    # Relationships
    educators = relationship("Educator", back_populates="institution")
    curriculum = relationship("Curriculum", back_populates="institutions")

class Educator(Base):
    __tablename__ = "educators"

    id = Column(UUID, primary_key=True, default=uuid.uuid4)
    name = Column(String, nullable=False)
    gender = Column(String)
    email = Column(String, unique=True, nullable=False)
    affiliation_code = Column(String, ForeignKey("institutions.affiliation_code"), nullable=False)
    verified = Column(Boolean, default=False)

    # Relationships
    institution = relationship("Institution", back_populates="educators")
    knowledge_bases = relationship("KnowledgeBase", back_populates="educator")
    question_papers = relationship("QuestionPaper", back_populates="created_by_educator")
    answer_sheets = relationship("AnswerSheet", back_populates="educator")

class KnowledgeBase(Base):
    __tablename__ = "knowledge_bases"

    id = Column(UUID, primary_key=True, default=uuid.uuid4)
    curriculum = Column(String, nullable=False)
    standard = Column(String, nullable=False)
    subject = Column(String, nullable=False)
    chapter = Column(String)
    file_url = Column(String, nullable=False)
    inserted_by = Column(UUID, ForeignKey("educators.id"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    educator = relationship("Educator", back_populates="knowledge_bases")

class QuestionPaper(Base):
    __tablename__ = "question_papers"

    id = Column(UUID, primary_key=True, default=uuid.uuid4)
    curriculum = Column(String, nullable=False)
    standard = Column(String, nullable=False)
    subject = Column(String, nullable=False)
    chapter = Column(String)
    file_url = Column(String)
    content = Column(JSON)
    created_by = Column(UUID, ForeignKey("educators.id"), nullable=False)
    downloaded_by = Column(ARRAY(UUID))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    created_by_educator = relationship("Educator", back_populates="question_papers")

class AnswerSheet(Base):
    __tablename__ = "answer_sheets"

    id = Column(UUID, primary_key=True, default=uuid.uuid4)
    student_name = Column(String, nullable=False)
    curriculum = Column(String, nullable=False)
    standard = Column(String, nullable=False)
    subject = Column(String, nullable=False)
    chapter = Column(String)
    file_url = Column(String, nullable=False)
    inserted_by = Column(UUID, ForeignKey("educators.id"))
    score = Column(Integer)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    educator = relationship("Educator", back_populates="answer_sheets")

class Curriculum(Base):
    __tablename__ = "curriculums"

    id = Column(UUID, primary_key=True, default=uuid.uuid4)
    curriculum = Column(String, nullable=False, unique=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    standards = relationship("Standard", back_populates="curriculum", cascade="all, delete-orphan")
    institutions = relationship("Institution", back_populates="curriculum")

class Standard(Base):
    __tablename__ = "standards"

    id = Column(UUID, primary_key=True, default=uuid.uuid4)
    curriculum_id = Column(UUID, ForeignKey("curriculums.id"), nullable=False)
    standard = Column(String, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    curriculum = relationship("Curriculum", back_populates="standards")
    subjects = relationship("Subject", back_populates="standard", cascade="all, delete-orphan")

    __table_args__ = (
        UniqueConstraint('curriculum_id', 'standard', name='unique_curriculum_standard'),
    )

class Subject(Base):
    __tablename__ = "subjects"

    id = Column(UUID, primary_key=True, default=uuid.uuid4)
    standard_id = Column(UUID, ForeignKey("standards.id"), nullable=False)
    subject = Column(String, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    standard = relationship("Standard", back_populates="subjects")
    topics = relationship("Topic", back_populates="subject", cascade="all, delete-orphan")

    __table_args__ = (
        UniqueConstraint('standard_id', 'subject', name='unique_standard_subject'),
    )

class Topic(Base):
    __tablename__ = "topics"

    id = Column(UUID, primary_key=True, default=uuid.uuid4)
    subject_id = Column(UUID, ForeignKey("subjects.id"), nullable=False)
    topic = Column(String, nullable=False)
    gcs_url = Column(String, nullable=True)  # URL of the bucket object for this topic
    extraction = Column(JSON, nullable=True)  # Dictionary containing extraction data
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    subject = relationship("Subject", back_populates="topics")

    __table_args__ = (
        UniqueConstraint('subject_id', 'topic', name='unique_subject_topic'),
    ) 