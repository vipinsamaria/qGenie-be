from fastapi import FastAPI, Depends, APIRouter
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from sqlalchemy import text
from db import Base, engine, get_db_session
from auth.routes import router as auth_router
from chat.routes import router as chat_router
from paper_props.routes import router as paper_props_router

app = FastAPI(
    title="qGenie API",
    description="Backend API for qGenie application",
    version="1.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_url="/api/openapi.json"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
async def startup():
    # Create database tables
    Base.metadata.create_all(bind=engine)

# Create API router with prefix
api_router = APIRouter(prefix="/api")

@api_router.get("/health/live")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy"}

@api_router.get("/health/ready")
async def test_db(db: Session = Depends(get_db_session)):
    """Test endpoint to verify database connection"""
    try:
        # Try to execute a simple query with proper text() wrapper
        db.execute(text("SELECT 1"))
        return {"status": "success", "message": "Database connection is working"}
    except Exception as e:
        return {"status": "error", "message": f"Database connection failed: {str(e)}"}

# Include the routers
app.include_router(api_router)
app.include_router(auth_router)
app.include_router(chat_router, prefix="/api")
app.include_router(paper_props_router, prefix="/api") 