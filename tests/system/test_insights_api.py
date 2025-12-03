# tests/system/test_insights_api.py
"""
System tests for the Insights API endpoints.

Tests the complete HTTP request/response cycle for:
- GET /api/insights/trend/{metric}/{resident_id}
- GET /api/insights/changepoints/{metric}/{resident_id}
- GET /api/insights/anomalies/{metric}/{resident_id}
"""


def test_get_trend_success(client, sample_resident, sample_30_days_data):
    """Should return trend data for resident with sufficient data"""
    response = client.get(f"/api/insights/trend/time_in_bed/{sample_resident.id}")

    assert response.status_code == 200
    data = response.json()

    # Check response structure
    assert "resident_id" in data
    assert "baseline_hours" in data
    assert "last_7_days_hours" in data
    assert "difference_hours" in data
    assert "description" in data

    # Check data values
    assert data["resident_id"] == sample_resident.id
    assert isinstance(data["baseline_hours"], str)
    assert "h" in data["baseline_hours"] or "min" in data["baseline_hours"]


def test_get_trend_resident_not_found(client):
    """Should return 404 for non-existent resident"""
    response = client.get("/api/insights/trend/time_in_bed/99999")

    assert response.status_code == 404


def test_get_trend_invalid_metric(client, sample_resident):
    """Should return 422 for invalid metric name"""
    response = client.get(f"/api/insights/trend/invalid_metric/{sample_resident.id}")

    assert response.status_code == 422


def test_get_changepoints_success(client, sample_resident, sample_30_days_data):
    """Should return changepoint data structure"""
    response = client.get(f"/api/insights/changepoints/time_in_bed/{sample_resident.id}")

    assert response.status_code == 200
    data = response.json()

    # Check response structure
    assert "resident_id" in data
    assert "metric" in data
    assert "n_change_points" in data
    assert "change_point_indices" in data
    assert "change_point_dates" in data
    assert "change_point_values" in data
    assert "description" in data

    # Check data types
    assert data["resident_id"] == sample_resident.id
    assert isinstance(data["n_change_points"], int)
    assert isinstance(data["change_point_indices"], list)


def test_get_changepoints_resident_not_found(client):
    """Should return 404 for non-existent resident"""
    response = client.get("/api/insights/changepoints/time_in_bed/99999")

    assert response.status_code == 404


def test_get_changepoints_invalid_metric(client, sample_resident):
    """Should return 422 for invalid metric"""
    response = client.get(f"/api/insights/changepoints/invalid_metric/{sample_resident.id}")

    assert response.status_code == 422


def test_get_anomalies_success(client, sample_resident, sample_30_days_data):
    """Should return anomaly detection structure"""
    response = client.get(f"/api/insights/anomalies/time_in_bed/{sample_resident.id}")

    assert response.status_code == 200
    data = response.json()

    # Check response structure
    assert "resident_id" in data
    assert "metric" in data
    assert "n_anomalies" in data
    assert "anomaly_indices" in data
    assert "anomaly_dates" in data
    assert "anomaly_values" in data
    assert "description" in data

    # Check data types
    assert data["resident_id"] == sample_resident.id
    assert isinstance(data["n_anomalies"], int)
    assert isinstance(data["anomaly_indices"], list)


def test_get_anomalies_resident_not_found(client):
    """Should return 404 for non-existent resident"""
    response = client.get("/api/insights/anomalies/time_in_bed/99999")

    assert response.status_code == 404


def test_get_anomalies_invalid_metric(client, sample_resident):
    """Should return 422 for invalid metric"""
    response = client.get(f"/api/insights/anomalies/invalid_metric/{sample_resident.id}")

    assert response.status_code == 422
