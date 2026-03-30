from pydantic import BaseModel


class OtpSendRequest(BaseModel):
    mobile_number: str


class OtpVerifyRequest(BaseModel):
    mobile_number: str
    otp: str
