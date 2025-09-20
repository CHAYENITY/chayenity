import enum
from typing import Optional, List
from decimal import Decimal
from datetime import datetime, date

from sqlalchemy import (
    Column,
    Integer,
    String,
    Enum,
    DateTime,
    Boolean,
    TEXT,
    DECIMAL,
    Date,
    ForeignKey,
    Numeric,
)
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from sqlmodel import SQLModel, Field

from app.database.base import Base


# * ====== Enum Definitions ======


class CityTierEnum(str, enum.Enum):
    MAIN = "MAIN"
    SECONDARY = "SECONDARY"


class UserTypeEnum(str, enum.Enum):
    TOURIST = "TOURIST"
    OPERATOR = "OPERATOR"


# * ====== Tables ======


class UserTravel(SQLModel, table=True):
    """ตารางเก็บข้อมูลแผนการเดินทางของผู้ใช้"""

    id: Optional[int] = Field(default=None, primary_key=True, index=True)
    user_id: int = Field(foreign_key="user.id")
    province_id: int = Field(foreign_key="province.id")

    start_date: date
    end_date: date
    notes: str = Field(default="")

    created_at: Optional[datetime] = Field(default=None)
    updated_at: Optional[datetime] = Field(default=None)


class Province(SQLModel, table=True):
    """ตารางเก็บข้อมูลจังหวัดและประเภทเมือง (หลัก/รอง)"""

    id: Optional[int] = Field(default=None, primary_key=True, index=True)
    name_th: str = Field(max_length=100, unique=True)
    name_en: Optional[str] = Field(default=None, max_length=100)
    region: str = Field(max_length=50)
    city_tier: CityTierEnum
    
    tax_reduction_rate: Decimal = Field(default=Decimal("0.00"), max_digits=4, decimal_places=2)
    tax_description: str = Field(default="")


class User(SQLModel, table=True):
    """ตารางสำหรับเก็บข้อมูลบัญชีผู้ใช้ร่วมกัน"""

    id: Optional[int] = Field(default=None, primary_key=True, index=True)
    email: str = Field(max_length=255, unique=True, index=True)
    phone_number: str = Field(max_length=15, unique=True)
    password_hash: str = Field(max_length=255)
    pin_hash: Optional[str] = Field(default=None, max_length=255)

    citizen_id: str = Field(max_length=13, unique=True, index=True)
    first_name_th: str = Field(max_length=100)
    last_name_th: str = Field(max_length=100)

    user_type: UserTypeEnum
    agreed_to_terms: bool = Field(default=False)
    is_active: bool = Field(default=True)

    created_at: Optional[datetime] = Field(default=None)
    updated_at: Optional[datetime] = Field(default=None)
