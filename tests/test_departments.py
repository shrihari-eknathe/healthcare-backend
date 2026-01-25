"""
Tests for Departments API.
"""


def test_create_department_success(client, auth_headers):
    """Test creating a department as admin."""
    response = client.post(
        "/departments",
        json={"name": "Cardiology"},
        headers=auth_headers
    )

    assert response.status_code == 201
    assert response.json["name"] == "Cardiology"


def test_list_departments(client, auth_headers):
    """Test listing departments."""
    # Create a department first
    client.post(
        "/departments",
        json={"name": "Neurology"},
        headers=auth_headers
    )

    # List departments
    response = client.get("/departments", headers=auth_headers)

    assert response.status_code == 200
    assert len(response.json) == 1
    assert response.json[0]["name"] == "Neurology"
