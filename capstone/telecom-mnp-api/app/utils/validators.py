import re

from fastapi import HTTPException, status


def validate_mobile_number(value: str) -> str:
    if not re.fullmatch(r"[6-9]\d{9}", value):
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Invalid mobile number")
    return value


def ensure_distinct_operators(current_operator: str, target_operator: str) -> None:
    if current_operator.strip().lower() == target_operator.strip().lower():
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Current and target operators must be different",
        )
