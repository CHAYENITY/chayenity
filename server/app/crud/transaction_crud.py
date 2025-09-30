"""
Transaction CRUD operations for Mock Payment System
"""

from typing import List, Optional, Tuple
from uuid import UUID, uuid4
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select, func, and_, or_, col

from app.models import Transaction, TransactionStatus, User, Gig, GigStatus
from app.schemas.transaction_schema import (
    TransactionCreateSchema,
    TransactionUpdateSchema,
    EscrowCreateSchema,
    ServiceFeeCalculationSchema,
    PaymentSummarySchema
)


class TransactionCRUD:
    """CRUD operations for Transaction with business logic"""
    
    @staticmethod
    def calculate_service_fee(amount: float, fee_rate: float = 0.05) -> ServiceFeeCalculationSchema:
        """Calculate service fee and net amount"""
        service_fee = round(amount * fee_rate, 2)
        net_amount = round(amount - service_fee, 2)
        
        return ServiceFeeCalculationSchema(
            base_amount=amount,
            service_fee_rate=fee_rate,
            service_fee_amount=service_fee,
            net_amount=net_amount
        )
    
    @staticmethod
    async def create_escrow(
        session: AsyncSession,
        gig_id: UUID,
        payer_id: UUID,
        payment_method: str = "mock_payment"
    ) -> Optional[Transaction]:
        """Create escrow transaction for a gig"""
        
        # Get gig details
        stmt = select(Gig).where(col(Gig.id) == gig_id)
        result = await session.execute(stmt)
        gig = result.scalar_one_or_none()
        
        if not gig:
            return None
        
        # Verify gig is accepted and has a helper
        if gig.status != GigStatus.ACCEPTED or not gig.helper_id:
            return None
        
        # Verify payer is the gig seeker
        if gig.seeker_id != payer_id:
            return None
        
        # Check if transaction already exists
        existing_stmt = select(Transaction).where(col(Transaction.gig_id) == gig_id)
        existing_result = await session.execute(existing_stmt)
        existing_transaction = existing_result.scalar_one_or_none()
        
        if existing_transaction:
            return None  # Transaction already exists
        
        # Calculate fees
        fee_calc = TransactionCRUD.calculate_service_fee(gig.budget)
        
        # Create transaction
        transaction = Transaction(
            gig_id=gig_id,
            payer_id=payer_id,
            payee_id=gig.helper_id,
            amount=gig.budget,
            service_fee=fee_calc.service_fee_amount,
            net_amount=fee_calc.net_amount,
            status=TransactionStatus.PENDING,
            payment_method=payment_method,
            transaction_ref=f"MOCK_{uuid4().hex[:8].upper()}"
        )
        
        session.add(transaction)
        await session.commit()
        await session.refresh(transaction)
        
        return transaction
    
    @staticmethod
    async def release_payment(
        session: AsyncSession,
        transaction_id: UUID,
        user_id: UUID
    ) -> Optional[Transaction]:
        """Release payment from escrow (complete transaction)"""
        
        # Get transaction
        stmt = select(Transaction).where(col(Transaction.id) == transaction_id)
        result = await session.execute(stmt)
        transaction = result.scalar_one_or_none()
        
        if not transaction:
            return None
        
        # Verify transaction is in pending status
        if transaction.status != TransactionStatus.PENDING:
            return None
        
        # Get gig to verify authorization
        gig_stmt = select(Gig).where(col(Gig.id) == transaction.gig_id)
        gig_result = await session.execute(gig_stmt)
        gig = gig_result.scalar_one_or_none()
        
        if not gig:
            return None
        
        # Only seeker (payer) or helper (payee) can release payment
        if user_id not in (transaction.payer_id, transaction.payee_id):
            return None
        
        # Update transaction status
        transaction.status = TransactionStatus.COMPLETED
        transaction.completed_at = datetime.utcnow()
        
        # Update gig status to completed if not already
        if gig.status != GigStatus.COMPLETED:
            gig.status = GigStatus.COMPLETED
            gig.completed_at = datetime.utcnow()
        
        await session.commit()
        await session.refresh(transaction)
        
        return transaction
    
    @staticmethod
    async def cancel_transaction(
        session: AsyncSession,
        transaction_id: UUID,
        user_id: UUID
    ) -> Optional[Transaction]:
        """Cancel a pending transaction"""
        
        # Get transaction
        stmt = select(Transaction).where(col(Transaction.id) == transaction_id)
        result = await session.execute(stmt)
        transaction = result.scalar_one_or_none()
        
        if not transaction:
            return None
        
        # Verify transaction is in pending status
        if transaction.status != TransactionStatus.PENDING:
            return None
        
        # Only payer can cancel
        if transaction.payer_id != user_id:
            return None
        
        # Update transaction status
        transaction.status = TransactionStatus.CANCELLED
        
        await session.commit()
        await session.refresh(transaction)
        
        return transaction
    
    @staticmethod
    async def get_transaction_by_id(
        session: AsyncSession,
        transaction_id: UUID
    ) -> Optional[Transaction]:
        """Get transaction by ID"""
        stmt = select(Transaction).where(col(Transaction.id) == transaction_id)
        result = await session.execute(stmt)
        return result.scalar_one_or_none()
    
    @staticmethod
    async def get_transaction_by_gig(
        session: AsyncSession,
        gig_id: UUID
    ) -> Optional[Transaction]:
        """Get transaction for a specific gig"""
        stmt = select(Transaction).where(col(Transaction.gig_id) == gig_id)
        result = await session.execute(stmt)
        return result.scalar_one_or_none()
    
    @staticmethod
    async def get_user_transactions(
        session: AsyncSession,
        user_id: UUID,
        skip: int = 0,
        limit: int = 20,
        status_filter: Optional[TransactionStatus] = None
    ) -> Tuple[List[Transaction], int]:
        """Get user's transactions (both as payer and payee)"""
        
        # Build query conditions
        conditions = or_(
            col(Transaction.payer_id) == user_id,
            col(Transaction.payee_id) == user_id
        )
        
        if status_filter:
            conditions = and_(conditions, col(Transaction.status) == status_filter)
        
        # Get transactions
        stmt = (
            select(Transaction)
            .where(conditions)
            .order_by(col(Transaction.created_at).desc())
            .offset(skip)
            .limit(limit)
        )
        result = await session.execute(stmt)
        transactions = result.scalars().all()
        
        # Get total count
        count_stmt = select(func.count(col(Transaction.id))).where(conditions)
        count_result = await session.execute(count_stmt)
        total = count_result.scalar() or 0
        
        return list(transactions), total
    
    @staticmethod
    async def get_payment_summary(
        session: AsyncSession,
        user_id: UUID
    ) -> PaymentSummarySchema:
        """Get payment summary statistics for a user"""
        
        # Get user info
        user_stmt = select(User).where(col(User.id) == user_id)
        user_result = await session.execute(user_stmt)
        user = user_result.scalar_one_or_none()
        
        if not user:
            return PaymentSummarySchema(
                user_id=user_id,
                user_name="Unknown User",
                total_transactions=0,
                total_amount_paid=0.0,
                total_amount_received=0.0,
                pending_transactions=0,
                completed_transactions=0
            )
        
        # Calculate totals for payments made (as payer)
        paid_stmt = (
            select(func.sum(col(Transaction.amount)))
            .where(
                and_(
                    col(Transaction.payer_id) == user_id,
                    col(Transaction.status) == TransactionStatus.COMPLETED
                )
            )
        )
        paid_result = await session.execute(paid_stmt)
        total_paid = paid_result.scalar() or 0.0
        
        # Calculate totals for payments received (as payee)
        received_stmt = (
            select(func.sum(col(Transaction.net_amount)))
            .where(
                and_(
                    col(Transaction.payee_id) == user_id,
                    col(Transaction.status) == TransactionStatus.COMPLETED
                )
            )
        )
        received_result = await session.execute(received_stmt)
        total_received = received_result.scalar() or 0.0
        
        # Count transactions by status
        pending_stmt = (
            select(func.count(col(Transaction.id)))
            .where(
                and_(
                    or_(
                        col(Transaction.payer_id) == user_id,
                        col(Transaction.payee_id) == user_id
                    ),
                    col(Transaction.status) == TransactionStatus.PENDING
                )
            )
        )
        pending_result = await session.execute(pending_stmt)
        pending_count = pending_result.scalar() or 0
        
        completed_stmt = (
            select(func.count(col(Transaction.id)))
            .where(
                and_(
                    or_(
                        col(Transaction.payer_id) == user_id,
                        col(Transaction.payee_id) == user_id
                    ),
                    col(Transaction.status) == TransactionStatus.COMPLETED
                )
            )
        )
        completed_result = await session.execute(completed_stmt)
        completed_count = completed_result.scalar() or 0
        
        total_transactions = pending_count + completed_count
        
        return PaymentSummarySchema(
            user_id=user_id,
            user_name=user.full_name,
            total_transactions=total_transactions,
            total_amount_paid=float(total_paid),
            total_amount_received=float(total_received),
            pending_transactions=pending_count,
            completed_transactions=completed_count
        )
    
    @staticmethod
    async def update_transaction_status(
        session: AsyncSession,
        transaction_id: UUID,
        new_status: TransactionStatus,
        user_id: UUID
    ) -> Optional[Transaction]:
        """Update transaction status (admin or authorized user only)"""
        
        # Get transaction
        stmt = select(Transaction).where(col(Transaction.id) == transaction_id)
        result = await session.execute(stmt)
        transaction = result.scalar_one_or_none()
        
        if not transaction:
            return None
        
        # Verify user is involved in the transaction
        if user_id not in (transaction.payer_id, transaction.payee_id):
            return None
        
        # Update status
        transaction.status = new_status
        
        if new_status == TransactionStatus.COMPLETED:
            transaction.completed_at = datetime.utcnow()
        
        await session.commit()
        await session.refresh(transaction)
        
        return transaction