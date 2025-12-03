# tests/conftest.py
"""
Shared test fixtures for all tests.

This file provides reusable test setup including:
- test_engine: SQLAlchemy engine for test database
- test_db: Fresh in-memory SQLite database session for each test
- client: TestClient with overridden database dependency
- sample_resident: Pre-created test resident (John Doe, room 101)
- sample_30_days_data: 30 days of stable bed sensor data (8h/day)

Fixtures are automatically available to all test files.
"""
from datetime import date, timedelta

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.database_config import Base
from app.dependencies import get_db
from app.main import app
from app.orm_models.inbed_daily import InBedDaily
from app.orm_models.resident import Resident


@pytest.fixture(scope="function")
def test_engine():
    """Create a test database engine"""
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(engine)
    yield engine
    Base.metadata.drop_all(engine)
    engine.dispose()


@pytest.fixture(scope="function")
def test_db(test_engine):
    """Create a test database session"""
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)
    session = TestingSessionLocal()
    yield session
    session.close()


@pytest.fixture(scope="function")
def client(test_db):
    """Create a test client with overridden database dependency"""

    def override_get_db():
        try:
            yield test_db
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


@pytest.fixture
def sample_resident(test_db):
    """Create a sample resident for testing"""
    resident = Resident(name="John Doe", room_number="101")
    test_db.add(resident)
    test_db.commit()
    test_db.refresh(resident)
    return resident


@pytest.fixture
def sample_30_days_data(test_db, sample_resident):
    """Create 30 days of stable bed sensor data"""
    for i in range(30):
        record = InBedDaily(
            date=date.today() - timedelta(days=29 - i),
            time_in_bed=28800,  # 8 hours
            at_rest=20000,
            low_activity=5000,
            high_activity=3800,
            times_out_bed_night=2,
            times_out_bed_day=1,
            resident_id=sample_resident.id,
        )
        test_db.add(record)
    test_db.commit()
