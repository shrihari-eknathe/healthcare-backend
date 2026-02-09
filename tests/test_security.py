"""
Security Tests - Testing the critical security fixes.

These tests verify:
1. Users cannot self-assign roles (always registered as MEMBER)
2. Only ADMIN can change user roles
3. Doctors can only manage their own availability
4. Double booking is prevented
"""


class TestRoleAssignmentSecurity:
    """Tests for role assignment security."""

    def test_register_always_member(self, client):
        """
        SECURITY: Users cannot choose their own role.
        Role field is not accepted - all users are registered as MEMBER.
        """
        # Register without role (correct way)
        response = client.post(
            "/auth/register",
            json={
                "email": "normaluser@test.com",
                "password": "password123"
            }
        )
        
        assert response.status_code == 201
        
        # Now login and verify we got a token
        login_response = client.post(
            "/auth/login",
            json={
                "email": "normaluser@test.com",
                "password": "password123"
            }
        )
        
        assert login_response.status_code == 200
        assert "access_token" in login_response.json

    def test_register_rejects_role_field(self, client):
        """
        SECURITY: If someone tries to pass a role field, it should be rejected.
        """
        response = client.post(
            "/auth/register",
            json={
                "email": "attacker@test.com",
                "password": "password123",
                "role": "ADMIN"  # Attacker tries to be admin
            }
        )
        
        # Should reject because 'role' is an unknown field
        assert response.status_code == 400
        assert "role" in str(response.json["error"]).lower()

    def test_only_admin_can_assign_roles(self, client, auth_headers, member_headers):
        """
        SECURITY: Only ADMIN can change user roles.
        MEMBER should not be able to change roles.
        """
        # First register a user
        client.post(
            "/auth/register",
            json={
                "email": "newuser@test.com",
                "password": "password123"
            }
        )
        
        # Get user ID (for simplicity, assume it's 3 after admin and member)
        # Admin tries to change role - should succeed
        response = client.patch(
            "/auth/users/3/role",
            json={"role": "DOCTOR"},
            headers=auth_headers
        )
        assert response.status_code == 200
        
        # Member tries to change role - should fail
        member_response = client.patch(
            "/auth/users/3/role",
            json={"role": "ADMIN"},
            headers=member_headers
        )
        assert member_response.status_code == 403


class TestDoctorOwnershipSecurity:
    """Tests for doctor ownership checks."""

    def test_doctor_can_manage_own_availability(self, client, auth_headers, doctor_headers, doctor_with_profile):
        """
        SECURITY: Doctor can create availability for themselves.
        """
        # Doctor creates availability for their own profile
        response = client.post(
            "/availability",
            json={
                "doctor_id": doctor_with_profile["doctor_id"],
                "date": "2026-04-01",
                "start_time": "09:00:00",
                "end_time": "09:30:00"
            },
            headers=doctor_headers
        )
        
        assert response.status_code == 201

    def test_doctor_cannot_manage_other_availability(self, client, auth_headers, doctor_headers, doctor_with_profile):
        """
        SECURITY: Doctor cannot create availability for another doctor.
        """
        # First, create another doctor (as admin)
        other_doctor = client.post(
            "/doctors",
            json={"name": "Dr. Other", "email": "other@hospital.com"},
            headers=auth_headers
        )
        other_doctor_id = other_doctor.json["id"]
        
        # Doctor tries to create availability for OTHER doctor - should fail
        response = client.post(
            "/availability",
            json={
                "doctor_id": other_doctor_id,
                "date": "2026-04-02",
                "start_time": "10:00:00",
                "end_time": "10:30:00"
            },
            headers=doctor_headers
        )
        
        assert response.status_code == 403
        assert "your own availability" in response.json["error"].lower()


class TestDoubleBookingPrevention:
    """Tests for race condition / double booking prevention."""

    def test_cannot_book_already_booked_slot(self, client, auth_headers, member_headers):
        """
        SECURITY: Cannot book a slot that is already booked.
        """
        # Create doctor and availability
        doctor_response = client.post(
            "/doctors",
            json={"name": "Dr. Race", "email": "race@hospital.com"},
            headers=auth_headers
        )
        doctor_id = doctor_response.json["id"]
        
        availability_response = client.post(
            "/availability",
            json={
                "doctor_id": doctor_id,
                "date": "2026-05-01",
                "start_time": "11:00:00",
                "end_time": "11:30:00"
            },
            headers=auth_headers
        )
        availability_id = availability_response.json["id"]
        
        # First booking - should succeed
        first_booking = client.post(
            "/appointments",
            json={"availability_id": availability_id},
            headers=member_headers
        )
        assert first_booking.status_code == 201
        
        # Second booking - should fail
        second_booking = client.post(
            "/appointments",
            json={"availability_id": availability_id},
            headers=member_headers
        )
        assert second_booking.status_code == 400
        assert "already booked" in second_booking.json["error"].lower()


class TestUnauthorizedAccess:
    """Tests for unauthorized access attempts."""

    def test_member_cannot_create_doctor(self, client, member_headers):
        """MEMBER should not be able to create doctors."""
        response = client.post(
            "/doctors",
            json={"name": "Fake Doctor", "email": "fake@hospital.com"},
            headers=member_headers
        )
        assert response.status_code == 403

    def test_member_cannot_create_availability(self, client, auth_headers, member_headers):
        """MEMBER should not be able to create availability."""
        # First create a doctor
        doctor = client.post(
            "/doctors",
            json={"name": "Dr. Test", "email": "test@hospital.com"},
            headers=auth_headers
        )
        doctor_id = doctor.json["id"]
        
        # Member tries to create availability - should fail
        response = client.post(
            "/availability",
            json={
                "doctor_id": doctor_id,
                "date": "2026-06-01",
                "start_time": "12:00:00",
                "end_time": "12:30:00"
            },
            headers=member_headers
        )
        assert response.status_code == 403
