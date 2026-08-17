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
    assert payload["token_type"] == "bearer"
    assert payload["role"] == "admin"
    assert payload["access_token"]


def test_admin_dashboard_requires_auth(client):
    unauthorized = client.get("/api/admin/dashboard")
    assert unauthorized.status_code == 401

    login = client.post(
        "/api/auth/login",
        data={"username": "admin", "password": "admin123"},
    ).json()

    response = client.get(
        "/api/admin/dashboard",
        headers={"Authorization": f"Bearer {login['access_token']}"},
    )
    assert response.status_code == 200
