from app.core.database import db


class OtpRepository:
    def upsert(self, mobile_number: str, payload: dict) -> dict:
        return db.otp_logs.upsert("mobile_number", mobile_number, payload)

    def get_by_mobile(self, mobile_number: str) -> dict | None:
        return db.otp_logs.find_one(mobile_number=mobile_number)
