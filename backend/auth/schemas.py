from pydantic import BaseModel, Field
from typing import List
from enum import Enum

class UserType(str, Enum):
    INSTITUTION = "institution"
    EDUCATOR = "educator"

class InstitutionType(str, Enum):
    INSTITUTE = "institute"
    SCHOOL = "school"

class CurriculumStandardPair(BaseModel):
    curriculum: str
    standard: str

class SubjectMappingPair(BaseModel):
    curriculum: str
    standard: str
    subject: str

class InstitutionSignupRequest(BaseModel):
    institutionType: InstitutionType
    instituteName: str
    district: str
    state: str
    country: str
    educators_count: int
    quota_remaining: int
    curriculum: dict

class EducatorSignupRequest(BaseModel):
    name: str
    email: str
    gender: str
    affiliation_code: str

class SignupResponse(BaseModel):
    affiliation_code: str | None = None
    success: bool
    message: str
    access_token: str | None = None

class OTPVerifyRequest(BaseModel):
    type: UserType
    email: str
    otp: str = Field(..., min_length=6, max_length=6)

class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int  # seconds until access token expires

class OTPVerifyResponse(BaseModel):
    success: bool
    message: str
    tokens: TokenResponse | None = None

class TokenRefreshRequest(BaseModel):
    refresh_token: str

class TokenRefreshResponse(BaseModel):
    success: bool
    message: str
    tokens: TokenResponse | None = None 