"""
Tests for Doctors API.
"""


def test_list_doctors(client, auth_headers):
    """Test listing doctors."""
    # Create a doctor first
    client.post(
        "/doctors",
        json={"name": "Dr. John Smith", "email": "john@hospital.com"},
        headers=auth_headers
    )

    # List doctors
    response = client.get("/doctors", headers=auth_headers)

    assert response.status_code == 200
    assert len(response.json) == 1
    assert response.json[0]["name"] == "Dr. John Smith"


def test_assign_doctor_to_department(client, auth_headers):
    """Test assigning a doctor to a department."""
    # Create a department
    dept_response = client.post(
        "/departments",
        json={"name": "Cardiology"},
        headers=auth_headers
    )
    department_id = dept_response.json["id"]

    # Create a doctor
    doctor_response = client.post(
        "/doctors",
        json={"name": "Dr. Jane Doe", "email": "jane@hospital.com"},
        headers=auth_headers
    )
    doctor_id = doctor_response.json["id"]

    # Assign doctor to department
    response = client.post(
        "/doctors/assign",
        json={"doctor_id": doctor_id, "department_id": department_id},
        headers=auth_headers
    )

    assert response.status_code == 200

    # Verify assignment
    list_response = client.get("/doctors", headers=auth_headers)
    assert list_response.json[0]["department"] == "Cardiology"
