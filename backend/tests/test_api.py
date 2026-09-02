def test_health(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_admin_login(client):
    response = client.post(
        "/api/auth/login",
        data={"username": "admin", "password": "admin123"},
    )
    assert response.status_code == 200
    payload = response.json()
    assert payload["role"] == "admin"
    assert "access_token" in payload


def test_admin_dashboard_requires_auth(client):
    unauthorized = client.get("/api/admin/dashboard")
    assert unauthorized.status_code == 401

    login = client.post(
        "/api/auth/login",
        data={"username": "admin", "password": "admin123"},
    )
    token = login.json()["access_token"]
    authorized = client.get(
        "/api/admin/dashboard",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert authorized.status_code == 200
    body = authorized.json()
    assert "total_students" in body
    assert "total_marks" in body


def test_faculty_login_and_dashboard(client):
    login = client.post(
        "/api/auth/login",
        data={"username": "faculty", "password": "faculty123"},
    )
    assert login.status_code == 200
    assert login.json()["role"] == "faculty"
    token = login.json()["access_token"]
    dash = client.get("/api/faculty/dashboard", headers={"Authorization": f"Bearer {token}"})
    assert dash.status_code == 200
    assert dash.json()["employee_code"] == "FAC-01"