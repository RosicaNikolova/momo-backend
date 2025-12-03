# tests/system/test_insights_edge_cases.py
"""
Edge case tests for insights endpoints.

Tests specific data scenarios like:
- Detecting actual anomalies
- Detecting change points with real breaks in data
- Insufficient data scenarios
"""
from datetime import date, timedelta

import pytest

from app.orm_models.inbed_daily import InBedDaily


@pytest.fixture
def resident_with_outlier(test_db, sample_resident):
    """Create 30 days of data with one obvious outlier"""
    for i in range(30):
        if i == 15:
            # Day 15: extreme outlier (only 2 hours of sleep)
            time_in_bed = 7200
        else:
            # Normal: around 8 hours
            time_in_bed = 28800

        record = InBedDaily(
            date=date.today() - timedelta(days=29 - i),
            time_in_bed=time_in_bed,
            at_rest=20000,
            low_activity=5000,
            high_activity=3800,
            times_out_bed_night=2,
            times_out_bed_day=1,
            resident_id=sample_resident.id,
        )
        test_db.add(record)
    test_db.commit()
    return sample_resident


@pytest.fixture
def resident_with_sleep_decline(test_db, sample_resident):
    """Create data with obvious decline: 23 days at 8h, then 7 days at 4h"""
    for i in range(30):
        if i < 23:
            time_in_bed = 28800  # 8 hours
        else:
            time_in_bed = 14400  # 4 hours (sudden drop!)

        record = InBedDaily(
            date=date.today() - timedelta(days=29 - i),
            time_in_bed=time_in_bed,
            at_rest=20000,
            low_activity=5000,
            high_activity=3800,
            times_out_bed_night=2,
            times_out_bed_day=1,
            resident_id=sample_resident.id,
        )
        test_db.add(record)
    test_db.commit()
    return sample_resident


@pytest.fixture
def resident_with_insufficient_data(test_db, sample_resident):
    """Create only 5 days of data (less than 7 needed for trend)"""
    for i in range(5):
        record = InBedDaily(
            date=date.today() - timedelta(days=4 - i),
            time_in_bed=28800,
            at_rest=20000,
            low_activity=5000,
            high_activity=3800,
            times_out_bed_night=2,
            times_out_bed_day=1,
            resident_id=sample_resident.id,
        )
        test_db.add(record)
    test_db.commit()
    return sample_resident


def test_anomaly_detects_outlier(client, resident_with_outlier):
    """Should detect the extreme outlier in otherwise normal data"""
    response = client.get(f"/api/insights/anomalies/time_in_bed/{resident_with_outlier.id}")

    assert response.status_code == 200
    data = response.json()
    assert data["n_anomalies"] >= 1  # Should catch the 2-hour night


def test_trend_detects_decline(client, resident_with_sleep_decline):
    """Should detect the sleep decline in last 7 days"""
    response = client.get(f"/api/insights/trend/time_in_bed/{resident_with_sleep_decline.id}")

    assert response.status_code == 200
    data = response.json()
    assert "decreased" in data["description"].lower()
    assert "3h" in data["difference_hours"]  # Should show ~3h decrease


def test_changepoint_detects_break(client, resident_with_sleep_decline):
    """Should detect the sudden change at day 23"""
    response = client.get(
        f"/api/insights/changepoints/time_in_bed/{resident_with_sleep_decline.id}"
    )

    assert response.status_code == 200
    data = response.json()
    assert data["n_change_points"] >= 1  # Should detect the break


def test_trend_insufficient_data(client, resident_with_insufficient_data):
    """Should return 404 when less than 7 days of data"""
    response = client.get(f"/api/insights/trend/time_in_bed/{resident_with_insufficient_data.id}")

    assert response.status_code == 404
