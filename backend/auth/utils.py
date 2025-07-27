import random
import string
from datetime import datetime, timedelta
from typing import Dict, Tuple, List
import jwt
from fastapi import HTTPException
import os
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import base64
from email.mime.text import MIMEText

# In-memory OTP store (replace with Redis in production)
otp_store: Dict[str, Dict] = {}

# JWT settings
JWT_SECRET = os.getenv("JWT_SECRET", "your-secret-key")  # Change in production
JWT_ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
REFRESH_TOKEN_EXPIRE_DAYS = 30

# Gmail API settings
SCOPES = ['https://www.googleapis.com/auth/gmail.send']

def get_gmail_service():
    """Get Gmail API service instance"""
    creds = None
    token_path = 'token.json'
    credentials_path = 'credentials.json'

    # Load existing token
    if os.path.exists(token_path):
        with open(token_path, 'r') as token:
            creds = Credentials.from_authorized_user_file(token_path, SCOPES)

    # Refresh token if expired
    if creds and creds.expired and creds.refresh_token:
        creds.refresh(Request())
    # Generate new token
    elif not creds:
        if not os.path.exists(credentials_path):
            raise HTTPException(
                status_code=500,
                detail="Gmail API credentials not found. Please set up Gmail API credentials."
            )
        flow = InstalledAppFlow.from_client_secrets_file(credentials_path, SCOPES)
        creds = flow.run_local_server(port=0)
        
        # Save token
        with open(token_path, 'w') as token:
            token.write(creds.to_json())

    try:
        return build('gmail', 'v1', credentials=creds)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create Gmail service: {str(e)}")

def generate_otp() -> str:
    """Generate a 6-digit OTP"""
    return ''.join(random.choices(string.digits, k=6))

def store_otp(email: str, otp: str, user_type: str):
    """Store OTP with expiry (5 minutes)"""
    otp_store[email] = {
        "otp": otp,
        "expires_at": datetime.utcnow() + timedelta(minutes=5),
        "type": user_type
    }

def verify_otp(email: str, otp: str, user_type: str) -> bool:
    """Verify OTP"""
    stored_data = otp_store.get(email)
    if not stored_data:
        return False
    
    if (stored_data["otp"] != otp or 
        stored_data["type"] != user_type or 
        stored_data["expires_at"] < datetime.utcnow()):
        return False
    
    # Clear OTP after successful verification
    del otp_store[email]
    return True

def generate_affiliation_code(name: str, district: str) -> str:
    """Generate a unique affiliation code for an institution."""
    # Take first 3 letters of name and district
    name_part = ''.join(c for c in name[:3] if c.isalnum()).upper()
    district_part = ''.join(c for c in district[:3] if c.isalnum()).upper()
    
    # Generate 4 random characters
    random_part = ''.join(random.choices(string.ascii_uppercase + string.digits, k=4))
    
    return f"{name_part}{district_part}{random_part}"

def create_tokens(data: dict) -> Tuple[str, str, int]:
    """Create access and refresh tokens"""
    # Access token
    access_token_expires = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token_data = {
        **data,
        "exp": access_token_expires,
        "token_type": "access"
    }
    access_token = jwt.encode(access_token_data, JWT_SECRET, algorithm=JWT_ALGORITHM)

    # Refresh token
    refresh_token_expires = datetime.utcnow() + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    refresh_token_data = {
        **data,
        "exp": refresh_token_expires,
        "token_type": "refresh"
    }
    refresh_token = jwt.encode(refresh_token_data, JWT_SECRET, algorithm=JWT_ALGORITHM)

    return access_token, refresh_token, ACCESS_TOKEN_EXPIRE_MINUTES * 60

def verify_refresh_token(refresh_token: str) -> dict:
    """Verify refresh token and return payload"""
    try:
        payload = jwt.decode(refresh_token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        if payload.get("token_type") != "refresh":
            raise HTTPException(status_code=400, detail="Invalid token type")
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Refresh token has expired")
    except jwt.JWTError:
        raise HTTPException(status_code=401, detail="Invalid refresh token")

async def send_otp_email(email: str, otp: str):
    """Send OTP via Gmail API"""
    try:
        service = get_gmail_service()
        
        # Create message
        message = MIMEText(f"""
        Your QGenie verification code is: {otp}
        
        This code will expire in 5 minutes.
        
        If you didn't request this code, please ignore this email.
        """)
        
        message['to'] = email
        message['subject'] = 'QGenie Verification Code'
        
        # Encode the message
        raw = base64.urlsafe_b64encode(message.as_bytes()).decode()
        
        try:
            # Send message
            service.users().messages().send(
                userId='me',
                body={'raw': raw}
            ).execute()
        except HttpError as error:
            raise HTTPException(
                status_code=500,
                detail=f"Failed to send email: {str(error)}"
            )
            
    except Exception as e:
        # For development, print OTP to console
        print(f"[DEV MODE] OTP for {email}: {otp}")
        # In production, you might want to log this error
        print(f"Error sending email: {str(e)}")
        # Don't raise exception in development to allow testing without email
        if os.getenv("ENV") == "production":
            raise HTTPException(
                status_code=500,
                detail="Failed to send OTP email"
            ) 