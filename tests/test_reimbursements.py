"""Tests for reimbursement module."""
import os

os.environ["FEATURE_REIMBURSEMENTS"] = "true"


def test_submit_reimbursement_claim(client, auth_headers, member_headers):
    """Member can submit a reimbursement claim with receipt."""
    # Create doctor and availability
    doctor = client.post(
        "/doctors",
        json={"name": "Dr. Claim", "email": "claim@hospital.com"},
        headers=auth_headers
    )
    doctor_id = doctor.json["id"]
    
    availability = client.post(
        "/availability",
        json={
            "doctor_id": doctor_id,
            "date": "2026-03-01",
            "start_time": "09:00:00",
            "end_time": "09:30:00"
        },
        headers=auth_headers
    )
    availability_id = availability.json["id"]
    
    # Book appointment
    appointment = client.post(
        "/appointments",
        json={"availability_id": availability_id},
        headers=member_headers
    )
    appointment_id = appointment.json["id"]
    
    # Mark appointment as completed
    from backend.appointments.models import Appointment
    from backend.common.db import db
    apt = db.session.get(Appointment, appointment_id)
    apt.status = "COMPLETED"
    db.session.commit()
    
    # Submit claim with receipt
    response = client.post(
        "/reimbursements",
        json={
            "appointment_id": appointment_id,
            "amount": 150.00,
            "receipt_url": "https://storage.example.com/receipts/12345.pdf",
            "description": "Medical consultation"
        },
        headers=member_headers
    )
    
    assert response.status_code == 201
    assert response.json["status"] == "PENDING"
    assert "receipt_url" in response.json


def test_claim_requires_receipt(client, auth_headers, member_headers):
    """Claim should fail without receipt_url."""
    doctor = client.post(
        "/doctors",
        json={"name": "Dr. NoReceipt", "email": "noreceipt@hospital.com"},
        headers=auth_headers
    )
    
    availability = client.post(
        "/availability",
        json={
            "doctor_id": doctor.json["id"],
            "date": "2026-03-04",
            "start_time": "14:00:00",
            "end_time": "14:30:00"
        },
        headers=auth_headers
    )
    
    appointment = client.post(
        "/appointments",
        json={"availability_id": availability.json["id"]},
        headers=member_headers
    )
    
    from backend.appointments.models import Appointment
    from backend.common.db import db
    apt = db.session.get(Appointment, appointment.json["id"])
    apt.status = "COMPLETED"
    db.session.commit()
    
    # Submit without receipt - should fail
    response = client.post(
        "/reimbursements",
        json={
            "appointment_id": appointment.json["id"],
            "amount": 100.00
        },
        headers=member_headers
    )
    
    assert response.status_code == 400
    assert "receipt_url" in str(response.json["error"]).lower()


def test_admin_approve_claim(client, auth_headers, member_headers):
    """Admin can approve a pending claim."""
    doctor = client.post(
        "/doctors",
        json={"name": "Dr. Approve", "email": "approve@hospital.com"},
        headers=auth_headers
    )
    
    availability = client.post(
        "/availability",
        json={
            "doctor_id": doctor.json["id"],
            "date": "2026-03-02",
            "start_time": "10:00:00",
            "end_time": "10:30:00"
        },
        headers=auth_headers
    )
    
    appointment = client.post(
        "/appointments",
        json={"availability_id": availability.json["id"]},
        headers=member_headers
    )
    
    from backend.appointments.models import Appointment
    from backend.common.db import db
    apt = db.session.get(Appointment, appointment.json["id"])
    apt.status = "COMPLETED"
    db.session.commit()
    
    claim = client.post(
        "/reimbursements",
        json={
            "appointment_id": appointment.json["id"],
            "amount": 200.00,
            "receipt_url": "https://storage.example.com/receipts/approved.pdf"
        },
        headers=member_headers
    )
    
    # Admin approves
    response = client.patch(
        f"/reimbursements/{claim.json['id']}/approve",
        json={"admin_notes": "Receipt verified"},
        headers=auth_headers
    )
    
    assert response.status_code == 200
    assert response.json["status"] == "APPROVED"


def test_admin_reject_claim(client, auth_headers, member_headers):
    """Admin can reject a pending claim."""
    doctor = client.post(
        "/doctors",
        json={"name": "Dr. Reject", "email": "reject@hospital.com"},
        headers=auth_headers
    )
    
    availability = client.post(
        "/availability",
        json={
            "doctor_id": doctor.json["id"],
            "date": "2026-03-03",
            "start_time": "11:00:00",
            "end_time": "11:30:00"
        },
        headers=auth_headers
    )
    
    appointment = client.post(
        "/appointments",
        json={"availability_id": availability.json["id"]},
        headers=member_headers
    )
    
    from backend.appointments.models import Appointment
    from backend.common.db import db
    apt = db.session.get(Appointment, appointment.json["id"])
    apt.status = "COMPLETED"
    db.session.commit()
    
    claim = client.post(
        "/reimbursements",
        json={
            "appointment_id": appointment.json["id"],
            "amount": 500.00,
            "receipt_url": "https://storage.example.com/receipts/fake.pdf"
        },
        headers=member_headers
    )
    
    # Admin rejects
    response = client.patch(
        f"/reimbursements/{claim.json['id']}/reject",
        json={"admin_notes": "Invalid receipt"},
        headers=auth_headers
    )
    
    assert response.status_code == 200
    assert response.json["status"] == "REJECTED"


def test_member_view_own_claims(client, auth_headers, member_headers):
    """Member can view their own claims."""
    response = client.get("/reimbursements/my", headers=member_headers)
    assert response.status_code == 200
    assert isinstance(response.json, list)
