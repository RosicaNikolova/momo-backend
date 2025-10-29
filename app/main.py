from fastapi import FastAPI, Depends
from .database_config import SessionLocal, Base, engine
from sqlalchemy import text
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

#


# def get_db():
#     db = SessionLocal()
#     try:
#         # return a value and then pause the function
#         yield db
#     finally:
#         db.close()

# Register routers
app.include_router(insights_router.router)
app.include_router(resident_router.router)

# Define a simple route


@app.get("/")
def read_root():
    return {"message": "FastAPI is running successfully!"}


# @app.get("/health/db")
# def health_db(db: Session = Depends(get_db)):
#     db.execute(text("SELECT 1"))   # simple test query
#     return {"db": "ok"}


@app.get("/data")
def get_data(db: Session = Depends(get_db)):
    records = db.query(InBedDaily).all()
    return records


@app.get("/resident")
def get_resident(db: Session = Depends(get_db)):
    records = db.query(Resident).all()
    return records
