import re
from typing import Optional


def validate_phone_number(v: str) -> str:
    if v is None:
        return None
    if not re.fullmatch(r"[0-9]{7,15}", v):
        raise ValueError(
            "Phone number must contain digits only (7-15 characters), no spaces or symbols"
        )
    return v.strip()


def validate_first_name(v: Optional[str]) -> Optional[str]:
    if not v or len(v.strip()) < 1:
        raise ValueError("First name is required")
    return v.strip()


def validate_last_name(v: Optional[str]) -> Optional[str]:
    if not v or len(v.strip()) < 1:
        raise ValueError("Last name is required")
    return v.strip()


def validate_email(email: str) -> str:
    return email.strip().lower()


def validate_password(password: str) -> str:
    if len(password) < 6:
        raise ValueError("Password must be at least 6 characters long")
    return password
