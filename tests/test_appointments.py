"""
Tests for Appointments API.
"""
import pytest


def test_book_appointment(client, auth_headers, member_headers):
    """Test booking an appointment as a member."""
    # Create a doctor (as admin)
    doctor_response = client.post(
        "/doctors",
        json={"name": "Dr. Brown", "email": "brown@hospital.com"},
        headers=auth_headers
    )
    doctor_id = doctor_response.json["id"]

    # Create availability slot (as admin/doctor)
    availability_response = client.post(
        "/availability",
        json={
            "doctor_id": doctor_id,
            "date": "2026-02-15",
            "start_time": "14:00:00",
            "end_time": "14:30:00"
        },
        headers=auth_headers
    )
    availability_id = availability_response.json["id"]

    # Book appointment (as member)
    response = client.post(
        "/appointments",
        json={"availability_id": availability_id},
        headers=member_headers
    )

    assert response.status_code == 201
    assert response.json["status"] == "SCHEDULED"
    assert "Appointment booked successfully" in response.json["message"]


def test_prevent_double_booking(client, auth_headers, member_headers):
    """Test that double booking is prevented."""
    # Create a doctor
    doctor_response = client.post(
        "/doctors",
        json={"name": "Dr. White", "email": "white@hospital.com"},
        headers=auth_headers
    )
    doctor_id = doctor_response.json["id"]

    # Create availability slot
    availability_response = client.post(
        "/availability",
        json={
            "doctor_id": doctor_id,
            "date": "2026-02-20",
            "start_time": "11:00:00",
            "end_time": "11:30:00"
        },
        headers=auth_headers
    )
    availability_id = availability_response.json["id"]

    # First booking (should succeed)
    first_booking = client.post(
        "/appointments",
        json={"availability_id": availability_id},
        headers=member_headers
    )
    assert first_booking.status_code == 201

    # Second booking (should fail - double booking)
    second_booking = client.post(
        "/appointments",
        json={"availability_id": availability_id},
        headers=member_headers
    )
    assert second_booking.status_code == 400
    assert "already booked" in second_booking.json["error"]
