def _create_operators(client, auth_headers):
    client.post("/api/operators", json={"name": "Airtel", "circle": "Tamil Nadu"}, headers=auth_headers["admin"])
    client.post("/api/operators", json={"name": "Jio", "circle": "Tamil Nadu"}, headers=auth_headers["admin"])


def test_full_porting_flow(client, auth_headers):
    _create_operators(client, auth_headers)

    create_response = client.post(
        "/api/port",
        json={
            "mobile_number": "9876543212",
            "current_operator": "Airtel",
            "target_operator": "Jio",
            "circle": "Tamil Nadu",
        },
        headers=auth_headers["customer"],
    )
    assert create_response.status_code == 201
    request_id = create_response.json()["id"]

    otp_response = client.post(
        "/api/otp/send",
        json={"mobile_number": "9876543212"},
        headers=auth_headers["customer"],
    )
    otp = otp_response.json()["otp"]
    verify_otp_response = client.post(
        "/api/otp/verify",
        json={"mobile_number": "9876543212", "otp": otp},
        headers=auth_headers["customer"],
    )
    assert verify_otp_response.status_code == 200

    upload_response = client.post(
        "/api/documents",
        json={
            "port_request_id": request_id,
            "type": "aadhaar",
            "file_url": "https://example.com/aadhaar.pdf",
        },
        headers=auth_headers["customer"],
    )
    assert upload_response.status_code == 201

    agent_verify = client.put(f"/api/port/{request_id}/verify", headers=auth_headers["agent"])
    assert agent_verify.status_code == 200
    assert agent_verify.json()["status"] == "verified"

    admin_approve = client.put(f"/api/admin/port/{request_id}/approve", headers=auth_headers["admin"])
    assert admin_approve.status_code == 200
    assert admin_approve.json()["port_request"]["status"] == "completed"

    reports = client.get("/api/admin/reports", headers=auth_headers["admin"])
    assert reports.status_code == 200
    assert reports.json()["status_breakdown"]["completed"] == 1
