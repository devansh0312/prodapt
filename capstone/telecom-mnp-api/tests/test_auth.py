def test_register_and_login_flow(client):
    register_response = client.post(
        "/api/auth/register",
        json={
            "name": "Customer One",
            "email": "customer1@example.com",
            "password": "password123",
            "mobile_number": "9876543219",
            "role": "customer",
        },
    )
    assert register_response.status_code == 200
    assert register_response.json()["user"]["role"] == "customer"

    login_response = client.post(
        "/api/auth/login",
        json={"email": "customer1@example.com", "password": "password123"},
    )
    assert login_response.status_code == 200
    assert "access_token" in login_response.json()
