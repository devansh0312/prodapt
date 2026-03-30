# Telecom MNP Backend

Fresh FastAPI backend for the Telecom Number Portability capstone. This implementation was created inside `capstone/telecom-mnp-api` and does not reuse the earlier exercises in the repository.

## Features

- JWT-style bearer authentication for `customer`, `agent`, and `admin`
- Role-based access control for telecom workflows
- Operator management
- Port request lifecycle: initiated -> OTP verified -> verified -> completed or rejected
- KYC document upload metadata
- OTP generation and verification
- Admin reports for request metrics
- Logging middleware and rate limiting
- File-backed local persistence for development and tests
- Docker assets for backend, MongoDB, and Redis containers

## Run

```bash
pip install -r requirements.txt
uvicorn app.main:app --reload
```

## Test

```bash
pytest
```
