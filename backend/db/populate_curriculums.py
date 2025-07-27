import sys
import os
from pathlib import Path

# Add the parent directory to sys.path
sys.path.append(str(Path(__file__).parent.parent))

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import IntegrityError
from db.models import Base, Curriculum
from db.config import settings
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Database connection URL
DATABASE_URL = f"postgresql://{settings.DB_USER}:{settings.DB_PASS}@{settings.DB_HOST}:{settings.DB_PORT}/{settings.DB_NAME}"

# Create database engine
engine = create_engine(DATABASE_URL)

# Create SessionLocal class
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def populate_curriculums():
    # Create a new session
    db = SessionLocal()
    
    # Data to be inserted
    curriculums_data = [
        {"curriculum": "CBSE"},
        {"curriculum": "ICSE"},
        {"curriculum": "IGCSE"}
    ]
    
    try:
        for curriculum_data in curriculums_data:
            # Check if curriculum already exists
            existing_curriculum = db.query(Curriculum).filter(
                Curriculum.curriculum == curriculum_data["curriculum"]
            ).first()
            
            if existing_curriculum:
                logger.info(f"Curriculum {curriculum_data['curriculum']} already exists.")
                continue
            
            # Create new curriculum
            new_curriculum = Curriculum(**curriculum_data)
            db.add(new_curriculum)
            logger.info(f"Adding curriculum: {curriculum_data['curriculum']}")
            
        # Commit the changes
        db.commit()
        logger.info("Successfully populated curriculums table.")
        
    except IntegrityError as e:
        logger.error(f"Error occurred while populating curriculums: {str(e)}")
        db.rollback()
    except Exception as e:
        logger.error(f"Unexpected error occurred: {str(e)}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    populate_curriculums() 