# schemas/province_schema.py
from sqlmodel import SQLModel
from typing import Optional
from decimal import Decimal

from app.models import CityTierEnum


# Base schema with common fields
class ProvinceBase(SQLModel):
    name_th: str
    name_en: Optional[str] = None
    region: str
    city_tier: CityTierEnum
    tax_reduction_rate: Decimal = Decimal("0.00")
    tax_description: str = ""


# Schema for creating provinces
class ProvinceCreate(ProvinceBase):
    pass


# Schema for updating provinces
class ProvinceUpdate(SQLModel):
    name_th: Optional[str] = None
    name_en: Optional[str] = None
    region: Optional[str] = None
    city_tier: Optional[CityTierEnum] = None
    tax_reduction_rate: Optional[Decimal] = None
    tax_description: Optional[str] = None


# Schema for returning province data
class ProvinceOut(ProvinceBase):
    id: int