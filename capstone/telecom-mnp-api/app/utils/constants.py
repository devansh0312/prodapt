from enum import Enum


class UserRole(str, Enum):
    customer = "customer"
    agent = "agent"
    admin = "admin"


class PortRequestStatus(str, Enum):
    initiated = "initiated"
    otp_verified = "otp_verified"
    verified = "verified"
    approved = "approved"
    rejected = "rejected"
    completed = "completed"


class DocumentType(str, Enum):
    aadhaar = "aadhaar"
    id_proof = "id_proof"
