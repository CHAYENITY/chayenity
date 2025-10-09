import enum
from datetime import datetime
from uuid import uuid4

from sqlalchemy import Column
from geoalchemy2 import Geometry
from sqlalchemy import String, Integer, Float, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship

from app.database.base import Base


# * === Enum Definitions ===


class GigStatus(str, enum.Enum):
    PENDING = "pending"
    ACCEPTED = "accepted"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class TransactionStatus(str, enum.Enum):
    PENDING = "pending"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    FAILED = "failed"


class MessageType(str, enum.Enum):
    TEXT = "text"
    IMAGE = "image"
    SYSTEM = "system"


# * === Core Entities ===


class User(Base):
    """User accounts for Hourz app - can be both Helper and Seeker"""

    __tablename__ = "user"
    id = Column(String, primary_key=True, default=lambda: str(uuid4()))
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)

    first_name = Column(String, nullable=True)
    last_name = Column(String, nullable=True)
    phone_number = Column(String, nullable=True)
    bio = Column(String, nullable=True)
    additional_contact = Column(String, nullable=True)
    profile_image_url = Column(String, nullable=True)

    is_profile_setup = Column(Boolean, default=False)
    is_available = Column(Boolean, default=False)
    is_verified = Column(Boolean, default=False)
    reputation_score = Column(Float, default=5.0)
    total_reviews = Column(Integer, default=0)

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow)

    address_id = Column(String, ForeignKey("address.id"), unique=True)

    address = relationship("Address", back_populates="user", uselist=False)
    # gigs_created = relationship("Gig", back_populates="seeker", foreign_keys="Gig.seeker_id")
    # gigs_accepted = relationship("Gig", back_populates="helper", foreign_keys="Gig.helper_id")
    # reviews_written = relationship(
    #     "Review", back_populates="reviewer", foreign_keys="Review.reviewer_id"
    # )
    # reviews_received = relationship(
    #     "Review", back_populates="reviewee", foreign_keys="Review.reviewee_id"
    # )
    # buddies = relationship("BuddyList", back_populates="user", foreign_keys="BuddyList.user_id")
    # buddy_of = relationship("BuddyList", back_populates="buddy", foreign_keys="BuddyList.buddy_id")
    # chat_participants = relationship("ChatParticipant", back_populates="user")
    # messages_sent = relationship("Message", back_populates="sender")
    # transactions_as_payer = relationship(
    #     "Transaction", back_populates="payer", foreign_keys="Transaction.payer_id"
    # )
    # transactions_as_payee = relationship(
    #     "Transaction", back_populates="payee", foreign_keys="Transaction.payee_id"
    # )
    # uploaded_files = relationship("UploadedFile", back_populates="uploader")

    # @property
    # def full_name(self) -> str:
    #     first = getattr(self, "first_name", None)
    #     last = getattr(self, "last_name", None)
    #     if not first and not last:
    #         return "Incomplete Profile"
    #     return f"{first or ''} {last or ''}".strip() or "Incomplete Profile"

    # @property
    # def current_address(self):
    #     return self.address


class Address(Base):
    """Address information for users"""

    __tablename__ = "address"
    id = Column(String, primary_key=True, default=lambda: str(uuid4()))
    address_line = Column(String, nullable=False)
    district = Column(String, nullable=False)
    province = Column(String, nullable=False)
    postal_code = Column(String, nullable=True)
    country = Column(String, default="Thailand")
    location = Column(Geometry("POINT", srid=4326), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="address", uselist=False)


# class Gig(Base):
#     """Gigs/Requests posted by Seekers"""

#     __tablename__ = "gig"
#     id = Column(String, primary_key=True, default=lambda: str(uuid4()))
#     title = Column(String, index=True, nullable=False)
#     description = Column(String, nullable=False)
#     duration_hours = Column(Integer, nullable=False)
#     budget = Column(Float, index=True, nullable=False)
#     location = Column(Geometry("POINT", srid=4326), nullable=False)
#     address_text = Column(String, nullable=False)
#     status = Column(String, default=GigStatus.PENDING.value, index=True)
#     image_urls = Column(JSON, nullable=True)
#     created_at = Column(DateTime, default=datetime.utcnow, index=True)
#     updated_at = Column(DateTime, default=datetime.utcnow)
#     starts_at = Column(DateTime, nullable=True)
#     completed_at = Column(DateTime, nullable=True)
#     seeker_id = Column(String, ForeignKey("user.id"), index=True, nullable=False)
#     helper_id = Column(String, ForeignKey("user.id"), index=True, nullable=True)
#     seeker = relationship("User", back_populates="gigs_created", foreign_keys=[seeker_id])
#     helper = relationship("User", back_populates="gigs_accepted", foreign_keys=[helper_id])
#     chat_room = relationship("ChatRoom", back_populates="gig", uselist=False)
#     reviews = relationship("Review", back_populates="gig")
#     transaction = relationship("Transaction", back_populates="gig", uselist=False)


# class ChatRoom(Base):
#     """Chat rooms created when gigs are accepted"""

#     __tablename__ = "chatroom"
#     id = Column(String, primary_key=True, default=lambda: str(uuid4()))
#     created_at = Column(DateTime, default=datetime.utcnow)
#     updated_at = Column(DateTime, default=datetime.utcnow)
#     is_active = Column(Boolean, default=True)
#     gig_id = Column(String, ForeignKey("gig.id"), unique=True, index=True)
#     gig = relationship("Gig", back_populates="chat_room")
#     participants = relationship("ChatParticipant", back_populates="chat_room")
#     messages = relationship("Message", back_populates="chat_room")


# class ChatParticipant(Base):
#     """Users participating in a chat room"""

#     __tablename__ = "chatparticipant"
#     id = Column(String, primary_key=True, default=lambda: str(uuid4()))
#     joined_at = Column(DateTime, default=datetime.utcnow)
#     last_read_at = Column(DateTime, nullable=True)
#     chat_room_id = Column(String, ForeignKey("chatroom.id"), index=True)
#     user_id = Column(String, ForeignKey("user.id"), index=True)
#     chat_room = relationship("ChatRoom", back_populates="participants")
#     user = relationship("User", back_populates="chat_participants")


# class Message(Base):
#     """Messages within chat rooms"""

#     __tablename__ = "message"
#     id = Column(String, primary_key=True, default=lambda: str(uuid4()))
#     content = Column(String, nullable=False)
#     message_type = Column(String, default=MessageType.TEXT.value)
#     image_url = Column(String, nullable=True)
#     is_read = Column(Boolean, default=False, index=True)
#     timestamp = Column(DateTime, default=datetime.utcnow, index=True)
#     chat_room_id = Column(String, ForeignKey("chatroom.id"), index=True)
#     sender_id = Column(String, ForeignKey("user.id"), index=True)
#     chat_room = relationship("ChatRoom", back_populates="messages")
#     sender = relationship("User", back_populates="messages_sent")


# class BuddyList(Base):
#     """Favorite helpers/seekers (buddy system)"""

#     __tablename__ = "buddylist"
#     id = Column(String, primary_key=True, default=lambda: str(uuid4()))
#     created_at = Column(DateTime, default=datetime.utcnow)
#     notes = Column(String, nullable=True)
#     user_id = Column(String, ForeignKey("user.id"), index=True)
#     buddy_id = Column(String, ForeignKey("user.id"), index=True)
#     user = relationship("User", back_populates="buddies", foreign_keys=[user_id])
#     buddy = relationship("User", back_populates="buddy_of", foreign_keys=[buddy_id])


# class Review(Base):
#     """Reviews and ratings after gig completion"""

#     __tablename__ = "review"
#     id = Column(String, primary_key=True, default=lambda: str(uuid4()))
#     rating = Column(Integer, nullable=False)
#     comment = Column(String, nullable=True)
#     created_at = Column(DateTime, default=datetime.utcnow)
#     gig_id = Column(String, ForeignKey("gig.id"), index=True)
#     reviewer_id = Column(String, ForeignKey("user.id"))
#     reviewee_id = Column(String, ForeignKey("user.id"))
#     gig = relationship("Gig", back_populates="reviews")
#     reviewer = relationship("User", back_populates="reviews_written", foreign_keys=[reviewer_id])
#     reviewee = relationship("User", back_populates="reviews_received", foreign_keys=[reviewee_id])


# class Transaction(Base):
#     """Mock payment transactions for gigs"""

#     __tablename__ = "transaction"
#     id = Column(String, primary_key=True, default=lambda: str(uuid4()))
#     amount = Column(Float, nullable=False)
#     service_fee = Column(Float, nullable=False)
#     net_amount = Column(Float, nullable=False)
#     currency = Column(String, default="THB")
#     status = Column(String, default=TransactionStatus.PENDING.value, index=True)
#     created_at = Column(DateTime, default=datetime.utcnow)
#     completed_at = Column(DateTime, nullable=True)
#     payment_method = Column(String, nullable=True)
#     transaction_ref = Column(String, nullable=True)
#     gig_id = Column(String, ForeignKey("gig.id"), unique=True, index=True)
#     payer_id = Column(String, ForeignKey("user.id"), index=True)
#     payee_id = Column(String, ForeignKey("user.id"), index=True)
#     gig = relationship("Gig", back_populates="transaction")
#     payer = relationship("User", back_populates="transactions_as_payer", foreign_keys=[payer_id])
#     payee = relationship("User", back_populates="transactions_as_payee", foreign_keys=[payee_id])


# class UploadedFile(Base):
#     """File upload tracking and metadata"""

#     __tablename__ = "uploadedfile"
#     id = Column(String, primary_key=True, default=lambda: str(uuid4()))
#     filename = Column(String, index=True, nullable=False)
#     original_filename = Column(String, nullable=False)
#     file_path = Column(String, nullable=False)
#     file_size = Column(Integer, nullable=False)
#     content_type = Column(String, nullable=False)
#     upload_category = Column(String, index=True, nullable=False)
#     uploaded_at = Column(DateTime, default=datetime.utcnow, index=True)
#     is_active = Column(Boolean, default=True, index=True)
#     uploaded_by = Column(String, ForeignKey("user.id"), index=True)
#     uploader = relationship("User", back_populates="uploaded_files")
