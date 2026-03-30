def test_send_and_verify_otp(client, auth_headers):
    send_response = client.post(
        "/api/otp/send",
        json={"mobile_number": "9876543212"},
        headers=auth_headers["customer"],
    )
    assert send_response.status_code == 200
    otp = send_response.json()["otp"]

    verify_response = client.post(
        "/api/otp/verify",
        json={"mobile_number": "9876543212", "otp": otp},
        headers=auth_headers["customer"],
    )
    assert verify_response.status_code == 200
    assert verify_response.json()["otp_log"]["verified"] is True
