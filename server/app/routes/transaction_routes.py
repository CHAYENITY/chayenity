"""
Transaction API routes for Mock Payment System
"""

from typing import List, Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.session import get_db
from app.security import get_current_user_with_access_token as get_current_user
from app.models import User, Transaction, TransactionStatus, Gig
from app.schemas.transaction_schema import (
    TransactionResponseSchema,
    EscrowCreateSchema,
    PaymentReleaseSchema,
    TransactionHistorySchema,
    ServiceFeeCalculationSchema,
    PaymentSummarySchema
)
from app.crud.transaction_crud import TransactionCRUD
from app.crud import user_crud as UserCRUD
from app.crud.gig_crud import GigCRUD

router = APIRouter(prefix="/transactions", tags=["transactions"])


def transaction_to_response(
    transaction: Transaction,
    gig_title: Optional[str] = None,
    payer_name: Optional[str] = None,
    payee_name: Optional[str] = None
) -> TransactionResponseSchema:
    """Convert Transaction model to response schema"""
    return TransactionResponseSchema(
        id=transaction.id,
        gig_id=transaction.gig_id,
        payer_id=transaction.payer_id,
        payee_id=transaction.payee_id,
        amount=transaction.amount,
        service_fee=transaction.service_fee,
        net_amount=transaction.net_amount,
        currency=transaction.currency,
        status=transaction.status,
        payment_method=transaction.payment_method,
        transaction_ref=transaction.transaction_ref,
        created_at=transaction.created_at,
        completed_at=transaction.completed_at,
        gig_title=gig_title,
        payer_name=payer_name,
        payee_name=payee_name
    )


@router.post("/escrow", response_model=TransactionResponseSchema)
async def create_escrow(
    escrow_data: EscrowCreateSchema,
    session: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create escrow transaction for a gig (hold payment)"""
    
    transaction = await TransactionCRUD.create_escrow(
        session,
        escrow_data.gig_id,
        current_user.id,
        escrow_data.payment_method or "mock_payment"
    )
    
    if not transaction:
        raise HTTPException(
            status_code=400,
            detail="Cannot create escrow. Gig must be accepted, you must be the gig seeker, "
                   "and no existing transaction should exist for this gig."
        )
    
    # Get additional data for response
    gig = await GigCRUD.get_gig_by_id(session, transaction.gig_id)
    payer = await UserCRUD.get_user_by_id(session, transaction.payer_id)
    payee = await UserCRUD.get_user_by_id(session, transaction.payee_id)
    
    return transaction_to_response(
        transaction,
        gig_title=gig.title if gig else None,
        payer_name=payer.full_name if payer else None,
        payee_name=payee.full_name if payee else None
    )


@router.put("/{transaction_id}/release", response_model=TransactionResponseSchema)
async def release_payment(
    transaction_id: UUID,
    session: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Release payment from escrow (complete transaction)"""
    
    transaction = await TransactionCRUD.release_payment(
        session,
        transaction_id,
        current_user.id
    )
    
    if not transaction:
        raise HTTPException(
            status_code=404,
            detail="Transaction not found, not in pending status, or you are not authorized to release it"
        )
    
    # Get additional data for response
    gig = await GigCRUD.get_gig_by_id(session, transaction.gig_id)
    payer = await UserCRUD.get_user_by_id(session, transaction.payer_id)
    payee = await UserCRUD.get_user_by_id(session, transaction.payee_id)
    
    return transaction_to_response(
        transaction,
        gig_title=gig.title if gig else None,
        payer_name=payer.full_name if payer else None,
        payee_name=payee.full_name if payee else None
    )


@router.put("/{transaction_id}/cancel", response_model=TransactionResponseSchema)
async def cancel_transaction(
    transaction_id: UUID,
    session: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Cancel a pending transaction (payer only)"""
    
    transaction = await TransactionCRUD.cancel_transaction(
        session,
        transaction_id,
        current_user.id
    )
    
    if not transaction:
        raise HTTPException(
            status_code=404,
            detail="Transaction not found, not in pending status, or you are not the payer"
        )
    
    # Get additional data for response
    gig = await GigCRUD.get_gig_by_id(session, transaction.gig_id)
    payer = await UserCRUD.get_user_by_id(session, transaction.payer_id)
    payee = await UserCRUD.get_user_by_id(session, transaction.payee_id)
    
    return transaction_to_response(
        transaction,
        gig_title=gig.title if gig else None,
        payer_name=payer.full_name if payer else None,
        payee_name=payee.full_name if payee else None
    )


@router.get("/{transaction_id}", response_model=TransactionResponseSchema)
async def get_transaction(
    transaction_id: UUID,
    session: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get transaction details by ID"""
    
    transaction = await TransactionCRUD.get_transaction_by_id(session, transaction_id)
    
    if not transaction:
        raise HTTPException(status_code=404, detail="Transaction not found")
    
    # Verify user is involved in the transaction
    if current_user.id not in (transaction.payer_id, transaction.payee_id):
        raise HTTPException(
            status_code=403,
            detail="You are not authorized to view this transaction"
        )
    
    # Get additional data for response
    gig = await GigCRUD.get_gig_by_id(session, transaction.gig_id)
    payer = await UserCRUD.get_user_by_id(session, transaction.payer_id)
    payee = await UserCRUD.get_user_by_id(session, transaction.payee_id)
    
    return transaction_to_response(
        transaction,
        gig_title=gig.title if gig else None,
        payer_name=payer.full_name if payer else None,
        payee_name=payee.full_name if payee else None
    )


@router.get("/gig/{gig_id}", response_model=TransactionResponseSchema)
async def get_gig_transaction(
    gig_id: UUID,
    session: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get transaction for a specific gig"""
    
    transaction = await TransactionCRUD.get_transaction_by_gig(session, gig_id)
    
    if not transaction:
        raise HTTPException(status_code=404, detail="No transaction found for this gig")
    
    # Verify user is involved in the transaction
    if current_user.id not in (transaction.payer_id, transaction.payee_id):
        raise HTTPException(
            status_code=403,
            detail="You are not authorized to view this transaction"
        )
    
    # Get additional data for response
    gig = await GigCRUD.get_gig_by_id(session, transaction.gig_id)
    payer = await UserCRUD.get_user_by_id(session, transaction.payer_id)
    payee = await UserCRUD.get_user_by_id(session, transaction.payee_id)
    
    return transaction_to_response(
        transaction,
        gig_title=gig.title if gig else None,
        payer_name=payer.full_name if payer else None,
        payee_name=payee.full_name if payee else None
    )


@router.get("/history/my", response_model=TransactionHistorySchema)
async def get_my_transaction_history(
    skip: int = Query(0, ge=0, description="Number of transactions to skip"),
    limit: int = Query(20, ge=1, le=50, description="Number of transactions to return"),
    status: Optional[TransactionStatus] = Query(None, description="Filter by transaction status"),
    session: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get current user's transaction history"""
    
    transactions, total = await TransactionCRUD.get_user_transactions(
        session, current_user.id, skip, limit, status
    )
    
    # Convert to response format and calculate totals
    transaction_responses = []
    total_paid = 0.0
    total_received = 0.0
    
    for transaction in transactions:
        # Get additional data
        gig = await GigCRUD.get_gig_by_id(session, transaction.gig_id)
        payer = await UserCRUD.get_user_by_id(session, transaction.payer_id)
        payee = await UserCRUD.get_user_by_id(session, transaction.payee_id)
        
        transaction_responses.append(transaction_to_response(
            transaction,
            gig_title=gig.title if gig else None,
            payer_name=payer.full_name if payer else None,
            payee_name=payee.full_name if payee else None
        ))
        
        # Calculate totals for completed transactions
        if transaction.status == TransactionStatus.COMPLETED:
            if transaction.payer_id == current_user.id:
                total_paid += transaction.amount
            if transaction.payee_id == current_user.id:
                total_received += transaction.net_amount
    
    return TransactionHistorySchema(
        transactions=transaction_responses,
        total_count=total,
        total_paid=total_paid,
        total_received=total_received
    )


@router.get("/summary/my", response_model=PaymentSummarySchema)
async def get_my_payment_summary(
    session: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get current user's payment summary statistics"""
    
    return await TransactionCRUD.get_payment_summary(session, current_user.id)


@router.post("/calculate-fee", response_model=ServiceFeeCalculationSchema)
async def calculate_service_fee(
    amount: float = Query(..., gt=0, description="Amount to calculate fee for"),
    fee_rate: float = Query(0.05, ge=0, le=1, description="Service fee rate (default 5%)")
):
    """Calculate service fee for a given amount"""
    
    return TransactionCRUD.calculate_service_fee(amount, fee_rate)


@router.put("/{transaction_id}/status", response_model=TransactionResponseSchema)
async def update_transaction_status(
    transaction_id: UUID,
    new_status: TransactionStatus,
    session: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update transaction status (for authorized users)"""
    
    transaction = await TransactionCRUD.update_transaction_status(
        session,
        transaction_id,
        new_status,
        current_user.id
    )
    
    if not transaction:
        raise HTTPException(
            status_code=404,
            detail="Transaction not found or you are not authorized to update it"
        )
    
    # Get additional data for response
    gig = await GigCRUD.get_gig_by_id(session, transaction.gig_id)
    payer = await UserCRUD.get_user_by_id(session, transaction.payer_id)
    payee = await UserCRUD.get_user_by_id(session, transaction.payee_id)
    
    return transaction_to_response(
        transaction,
        gig_title=gig.title if gig else None,
        payer_name=payer.full_name if payer else None,
        payee_name=payee.full_name if payee else None
    )