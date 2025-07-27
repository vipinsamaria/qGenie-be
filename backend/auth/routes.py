from fastapi import APIRouter, Depends, Request, HTTPException
from sqlalchemy.orm import Session
from db.database import get_db_session
from db.models import Institution, Educator
from auth.schemas import (
    InstitutionSignupRequest, EducatorSignupRequest, SignupResponse
)
from .firebase_utils import verify_firebase_token, delete_firebase_user
from typing import Literal
from pydantic import BaseModel
from .jwt_utils import create_access_token
import json

router = APIRouter(prefix="/api/auth", tags=["Authentication"])

class LoginResponse(BaseModel):
    user_type: Literal["institution", "educator"]
    user_details: dict
    message: str
    access_token: str

@router.post("/signup/institution", response_model=SignupResponse)
def signup_institution(
    payload: InstitutionSignupRequest,
    request: Request,
    db: Session = Depends(get_db_session)
):
    try:
        user = verify_firebase_token(request)
        email = user["email"]
        uid = user["uid"]  # Get Firebase UID for potential rollback
        
        # Check if institution with username already exists
        existing_institution = db.query(Institution).filter(
            Institution.email == email
        ).first()
        if existing_institution:
            # Delete Firebase user since we can't use this email
            delete_firebase_user(uid)
            raise HTTPException(status_code=400, detail="Institution already registered")

        # Generate affiliation code
        from auth.utils import generate_affiliation_code
        affiliation_code = generate_affiliation_code(payload.instituteName, payload.district)

        # Create institution
        institution = Institution(
            type=payload.institutionType,
            affiliation_code=affiliation_code,
            email=email,
            name=payload.instituteName,
            district=payload.district,
            state=payload.state,
            country=payload.country,
            educators_count=payload.educators_count,
            quota_remaining=payload.quota_remaining,
            curriculum_id=payload.curriculum["id"]
        )
        db.add(institution)
        db.commit()

        # Create access token
        token_data = {
            "sub": str(institution.id),
            "email": email,
            "type": "institution"
        }
        access_token = create_access_token(token_data)

        return SignupResponse(
            success=True,
            message="Institution registered successfully.",
            affiliation_code=affiliation_code,
            access_token=access_token
        )
        
    except Exception as e:
        db.rollback()  # Rollback database changes
        # If we have a uid and this isn't an already-registered error
        if 'uid' in locals() and not (
            isinstance(e, HTTPException) and 
            e.status_code == 400 and 
            "already registered" in str(e.detail)
        ):
            delete_firebase_user(uid)  # Delete the Firebase user
        raise  # Re-raise the exception

@router.post("/signup/educator", response_model=SignupResponse)
def signup_educator(
    payload: EducatorSignupRequest,
    request: Request,
    db: Session = Depends(get_db_session)
):
    try:
        user = verify_firebase_token(request)
        email = user["email"]
        uid = user["uid"]  # Get Firebase UID for potential rollback

        # Check if educator with email already exists
        existing_educator = db.query(Educator).filter(
            Educator.email == email
        ).first()
        if existing_educator:
            # Delete Firebase user since we can't use this email
            delete_firebase_user(uid)
            raise HTTPException(status_code=400, detail="Educator already registered")

        # Verify affiliation code
        institution = db.query(Institution).filter(
            Institution.affiliation_code == payload.affiliation_code
        ).first()
        if not institution:
            # Delete Firebase user since the affiliation is invalid
            delete_firebase_user(uid)
            raise HTTPException(status_code=400, detail="Invalid affiliation code")

        # Create educator
        educator = Educator(
            name=payload.name,
            email=email,
            gender=payload.gender,
            affiliation_code=payload.affiliation_code
        )
        db.add(educator)
        db.commit()

        token_data = {
            "sub": str(educator.id),
            "email": email,
            "type": "educator"
        }
        access_token = create_access_token(token_data)

        return SignupResponse(
            success=True,
            access_token=access_token,
            message="Educator registered successfully."
        )
        
    except Exception as e:
        db.rollback()  # Rollback database changes
        # If we have a uid and this isn't an already-registered error
        if 'uid' in locals() and not (
            isinstance(e, HTTPException) and 
            e.status_code == 400 and 
            "already registered" in str(e.detail)
        ):
            delete_firebase_user(uid)  # Delete the Firebase user
        raise  # Re-raise the exception

@router.post("/login", response_model=LoginResponse)
async def login(request: Request, db: Session = Depends(get_db_session)):
    """
    Verify Firebase token and return user details with internal access token.
    The frontend should send the Firebase ID token in the Authorization header.
    """
    user = verify_firebase_token(request)
    email = user["email"]

    # Check if user is an institution
    institution = db.query(Institution).filter(Institution.email == email).first()
    if institution:
        # Create internal access token
        token_data = {
            "sub": str(institution.id),
            "email": email,
            "type": "institution"
        }
        access_token = create_access_token(token_data)
        
        return LoginResponse(
            user_type="institution",
            user_details={
                "id": str(institution.id),
                "name": institution.name,
                "type": institution.type,
                "affiliation_code": institution.affiliation_code,
                "district": institution.district,
                "state": institution.state,
                "country": institution.country,
                "educators_count": institution.educators_count,
                "quota_remaining": institution.quota_remaining
            },
            message="Institution login successful",
            access_token=access_token
        )

    # Check if user is an educator
    educator = db.query(Educator).filter(Educator.email == email).first()
    if educator:
        # Create internal access token
        token_data = {
            "sub": str(educator.id),
            "email": email,
            "type": "educator"
        }
        access_token = create_access_token(token_data)

        return LoginResponse(
            user_type="educator",
            user_details={
                "id": str(educator.id),
                "name": educator.name,
                "email": educator.email,
                "gender": educator.gender,
                "affiliation_code": educator.affiliation_code
            },
            message="Educator login successful",
            access_token=access_token
        )

    raise HTTPException(status_code=404, detail="User not found. Please sign up first.") 
