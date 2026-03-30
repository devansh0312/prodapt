def test_admin_can_create_operator(client, auth_headers):
    response = client.post(
        "/api/operators",
        json={"name": "Airtel", "circle": "Tamil Nadu"},
        headers=auth_headers["admin"],
    )
    assert response.status_code == 201
    assert response.json()["name"] == "Airtel"


def test_customer_cannot_create_operator(client, auth_headers):
    response = client.post(
        "/api/operators",
        json={"name": "Jio", "circle": "Tamil Nadu"},
        headers=auth_headers["customer"],
    )
    assert response.status_code == 403
