from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from .database_config import Base, engine
from sqlalchemy.orm import Session
from contextlib import asynccontextmanager
from app.orm_models.inbed_daily import InBedDaily
from app.orm_models.resident import Resident  # ensure Resident is imported
from app.routers import insights_router, resident_router
from app.dependencies import get_db


@asynccontextmanager
async def lifespan(app: FastAPI):
    # runs once at startup
    Base.metadata.create_all(bind=engine)
    yield
    # runs once at shutdown (optional cleanup)


# Initialize app
app = FastAPI(lifespan=lifespan)

# Configure CORS
origins = [
    "http://localhost:3000",  # React default port
    "http://localhost:5173",  # Vite default port
    "http://127.0.0.1:3000",
    "http://127.0.0.1:5173",
    "http://localhost:8080",  # Additional common frontend port
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],
)

# Register routers
app.include_router(insights_router.router)
app.include_router(resident_router.router)


@app.get("/")
def read_root():
    return {"message": "FastAPI is running successfully!"}
