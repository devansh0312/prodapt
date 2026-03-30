import sys
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app.main import app


@pytest.fixture(autouse=True)
def reset_file_db():
    data_dir = Path(__file__).resolve().parents[1] / "data"
    data_dir.mkdir(parents=True, exist_ok=True)
    for filename in ["users.json", "operators.json", "port_requests.json", "documents.json", "otp_logs.json"]:
        (data_dir / filename).write_text("[]", encoding="utf-8")
    yield


@pytest.fixture
def client():
    return TestClient(app)


def register_and_login(client: TestClient, name: str, email: str, role: str, mobile_number: str) -> dict:
    response = client.post(
        "/api/auth/register",
        json={
            "name": name,
            "email": email,
            "password": "password123",
            "mobile_number": mobile_number,
            "role": role,
        },
    )
    return response.json()


@pytest.fixture
def auth_headers(client: TestClient):
    admin = register_and_login(client, "Admin User", "admin@example.com", "admin", "9876543210")
    agent = register_and_login(client, "Agent User", "agent@example.com", "agent", "9876543211")
    customer = register_and_login(client, "Customer User", "customer@example.com", "customer", "9876543212")
    return {
        "admin": {"Authorization": f"Bearer {admin['access_token']}"},
        "agent": {"Authorization": f"Bearer {agent['access_token']}"},
        "customer": {"Authorization": f"Bearer {customer['access_token']}"},
    }
