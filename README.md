# Momo Backend - Bedsense Data Insights API

FastAPI backend that transforms bed sensor data from Momo Medical's Bedsense system, using statistical data analysys, into actionable insights for caregivers in elderly care homes.

## Features

- **Sleep Trend Analysis**: Compare recent sleep patterns (7 days) against 28-day baseline
- **Anomaly Detection**: Identify unusual sleep behavior using z-score analysis
- **Change Point Detection**: Discover sudden shifts in sleep patterns with PELT algorithm
- **Resident Management**: CRUD operations for managing residents

## Tech Stack

- **Backend**: FastAPI, SQLAlchemy, SQLite
- **Analysis**: pandas, NumPy, SciPy, ruptures
- **Testing**: pytest (85%+ coverage)
- **Code Quality**: Ruff, Black, MyPy
- **CI/CD**: GitHub Actions, SonarCloud

## Quick Start
```bash
# Clone repository
git clone https://github.com/RosicaNikolova/momo-backend.git
cd momo-backend

# Create virtual environment
python -m venv .venv
.venv\Scripts\activate  # Windows
source .venv/bin/activate  # macOS/Linux

# Install dependencies
pip install -r requirements.txt

# Run application
uvicorn app.main:app --reload
```

API available at: `http://localhost:8000`  
Documentation: `http://localhost:8000/docs`

## API Endpoints

### Residents
- `GET /api/residents/` - List all residents
- `GET /api/residents/{id}` - Get resident by ID

### Insights
- `GET /api/insights/trend/{metric}/{resident_id}` - Get sleep trend
- `GET /api/insights/changepoints/{metric}/{resident_id}` - Detect change points
- `GET /api/insights/anomalies/{metric}/{resident_id}` - Detect anomalies

**Supported metrics**: `time_in_bed`, `at_rest`, `low_activity`, `high_activity`

## Project Structure
```
momo-backend/
├── app/
│   ├── main.py                 # FastAPI app
│   ├── orm_models/             # Database models
│   ├── schemas/                # Pydantic DTOs
│   ├── routers/                # API endpoints
│   ├── services/               # Business logic
│   └── repository/             # Data access
├── tests/                      # Test suite (85%+ coverage)
├── .github/workflows/ci.yml    # CI/CD pipeline
└── pyproject.toml              # Configuration
```

## Testing

- **Coverage**: 85%+
- **Routers**: 100%
- **Services**: 88-100%
- **Repositories**: 92-100%

## CI/CD Pipeline

Automated pipeline runs on push/PR to `main` or `develop`:
1. Build and install dependencies
2. Run pytest with coverage
3. Code quality checks (Ruff, Black, MyPy)
4. SonarCloud analysis

## About

Graduation project developed at Futures Lab (MindLabs Tilburg) in collaboration with Momo Medical to help caregivers make data-driven decisions therefore improve residents wellbeing.

**Developer**: Rositsa Nikolova  
**Organization**: Futures Lab, MindLabs Tilburg  
**Partner**: Momo Medical

---
