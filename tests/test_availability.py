"""
Tests for Availability API.
"""


def test_create_availability(client, auth_headers):
    """Test creating an availability slot."""
    # First create a doctor
    doctor_response = client.post(
        "/doctors",
        json={"name": "Dr. Smith", "email": "smith@hospital.com"},
        headers=auth_headers
    )
    doctor_id = doctor_response.json["id"]

    # Create availability slot
    response = client.post(
        "/availability",
        json={
            "doctor_id": doctor_id,
            "date": "2026-02-01",
            "start_time": "09:00:00",
            "end_time": "09:30:00"
        },
        headers=auth_headers
    )

    assert response.status_code == 201
    assert response.json["doctor_id"] == doctor_id
    assert response.json["is_booked"] == False


def test_get_doctor_availability(client, auth_headers):
    """Test getting a doctor's availability."""
    # Create a doctor
    doctor_response = client.post(
        "/doctors",
        json={"name": "Dr. Jane", "email": "jane@hospital.com"},
        headers=auth_headers
    )
    doctor_id = doctor_response.json["id"]

    # Create availability slot
    client.post(
        "/availability",
        json={
            "doctor_id": doctor_id,
            "date": "2026-02-01",
            "start_time": "10:00:00",
            "end_time": "10:30:00"
        },
        headers=auth_headers
    )

    # Get availability
    response = client.get(
        f"/availability/doctor/{doctor_id}",
        headers=auth_headers
    )

    assert response.status_code == 200
    assert len(response.json) == 1
    assert response.json[0]["doctor_id"] == doctor_id
