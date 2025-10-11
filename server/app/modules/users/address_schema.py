# schemas/address_schema.py
from pydantic import BaseModel
from typing import Optional


class AddressBase(BaseModel):
    address_line: str
    district: str
    province: str
    country: str = "Thailand"
    postal_code: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
