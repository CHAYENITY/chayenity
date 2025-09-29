"""
Transaction schemas for Mock Payment System
"""

from typing import Optional, List
from datetime import datetime
from uuid import UUID
from pydantic import BaseModel, Field, ConfigDict

from app.models import TransactionStatus


class TransactionCreateSchema(BaseModel):
    """Schema for creating a new transaction (escrow)"""
    gig_id: UUID = Field(..., description="ID of the gig being paid for")
    amount: float = Field(..., gt=0, description="Total transaction amount in THB")
    payment_method: Optional[str] = Field("mock_payment", description="Payment method (mock)")
    
    
class TransactionUpdateSchema(BaseModel):
    """Schema for updating transaction status"""
    status: TransactionStatus = Field(..., description="New transaction status")
    transaction_ref: Optional[str] = Field(None, description="External transaction reference")


class TransactionResponseSchema(BaseModel):
    """Schema for transaction responses"""
    id: UUID
    gig_id: UUID
    payer_id: UUID
    payee_id: UUID
    amount: float
    service_fee: float
    net_amount: float
    currency: str
    status: TransactionStatus
    payment_method: Optional[str] = None
    transaction_ref: Optional[str] = None
    created_at: datetime
    completed_at: Optional[datetime] = None
    
    # Related data
    gig_title: Optional[str] = None
    payer_name: Optional[str] = None
    payee_name: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


class EscrowCreateSchema(BaseModel):
    """Schema for creating escrow (holding payment)"""
    gig_id: UUID = Field(..., description="ID of the gig to create escrow for")
    payment_method: Optional[str] = Field("mock_payment", description="Payment method")


class PaymentReleaseSchema(BaseModel):
    """Schema for releasing payment from escrow"""
    transaction_id: UUID = Field(..., description="ID of the transaction to release")
    release_reason: Optional[str] = Field(None, description="Reason for release")


class TransactionHistorySchema(BaseModel):
    """Schema for transaction history response"""
    transactions: List[TransactionResponseSchema]
    total_count: int
    total_paid: float
    total_received: float
    currency: str = "THB"


class ServiceFeeCalculationSchema(BaseModel):
    """Schema for service fee calculation"""
    base_amount: float
    service_fee_rate: float = Field(0.05, description="Service fee rate (5%)")
    service_fee_amount: float
    net_amount: float
    currency: str = "THB"


class PaymentSummarySchema(BaseModel):
    """Schema for payment summary statistics"""
    user_id: UUID
    user_name: str
    total_transactions: int
    total_amount_paid: float
    total_amount_received: float
    pending_transactions: int
    completed_transactions: int
    currency: str = "THB"