import firebase_admin
from firebase_admin import credentials, auth
from fastapi import HTTPException, Request
import os

# Initialize Firebase app only once
if not firebase_admin._apps:
    cred = credentials.Certificate(os.getenv("FIREBASE_SERVICE_ACCOUNT", "firebase_service_account.json"))
    firebase_admin.initialize_app(cred)

def verify_firebase_token(request: Request):
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing or invalid Authorization header")
    id_token = auth_header.split(" ")[1]
    try:
        decoded_token = auth.verify_id_token(id_token)
        return decoded_token
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid Firebase ID token")

def delete_firebase_user(uid: str) -> bool:
    """Delete a Firebase user by their UID.
    
    Args:
        uid: The Firebase UID of the user to delete
        
    Returns:
        bool: True if deletion was successful, False otherwise
        
    Raises:
        HTTPException: If there's an error deleting the user
    """
    try:
        auth.delete_user(uid)
        return True
    except auth.UserNotFoundError:
        return False  # User already deleted
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to delete Firebase user: {str(e)}"
        ) 