import enum
from typing import Optional, List, Any
from datetime import datetime
from uuid import UUID, uuid4

from sqlalchemy import Column
from sqlalchemy import JSON
from geoalchemy2 import Geometry
from sqlmodel import SQLModel, Field, Relationship


# === Enum Definitions ===


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


# === Core Entities ===


class User(SQLModel, table=True):
    """User accounts for Hourz app - can be both Helper and Seeker"""

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    email: str = Field(unique=True, index=True)
    hashed_password: str
    full_name: str
    profile_image_url: Optional[str] = None
    contact_info: Optional[str] = None  # phone or LINE ID

    # Location for Helper mode (fixed location)
    fixed_location: Optional[Any] = Field(
        default=None, sa_column=Column(Geometry("POINT", srid=4326))
    )
    address_text: Optional[str] = None

    # Helper availability
    is_available: bool = Field(default=False)  # Helper availability toggle

    # Profile and reputation
    is_verified: bool = Field(default=False)
    reputation_score: float = Field(default=5.0)
    total_reviews: int = Field(default=0)

    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationships
    gigs_created: List["Gig"] = Relationship(
        back_populates="seeker", sa_relationship_kwargs={"foreign_keys": "Gig.seeker_id"}
    )
    gigs_accepted: List["Gig"] = Relationship(
        back_populates="helper", sa_relationship_kwargs={"foreign_keys": "Gig.helper_id"}
    )
    reviews_written: List["Review"] = Relationship(
        back_populates="reviewer", sa_relationship_kwargs={"foreign_keys": "Review.reviewer_id"}
    )
    reviews_received: List["Review"] = Relationship(
        back_populates="reviewee", sa_relationship_kwargs={"foreign_keys": "Review.reviewee_id"}
    )
    buddies: List["BuddyList"] = Relationship(
        back_populates="user", sa_relationship_kwargs={"foreign_keys": "BuddyList.user_id"}
    )
    buddy_of: List["BuddyList"] = Relationship(
        back_populates="buddy", sa_relationship_kwargs={"foreign_keys": "BuddyList.buddy_id"}
    )
    chat_participants: List["ChatParticipant"] = Relationship(back_populates="user")
    messages_sent: List["Message"] = Relationship(back_populates="sender")
    transactions_as_payer: List["Transaction"] = Relationship(
        back_populates="payer", sa_relationship_kwargs={"foreign_keys": "Transaction.payer_id"}
    )
    transactions_as_payee: List["Transaction"] = Relationship(
        back_populates="payee", sa_relationship_kwargs={"foreign_keys": "Transaction.payee_id"}
    )
    uploaded_files: List["UploadedFile"] = Relationship(back_populates="uploader")


class Gig(SQLModel, table=True):
    """Gigs/Requests posted by Seekers"""

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    title: str = Field(index=True)
    description: str
    duration_hours: int  # Expected duration in hours
    budget: float = Field(index=True)  # Budget in local currency

    # Location where gig needs to be done (GPS pinned by Seeker)
    location: Any = Field(sa_column=Column(Geometry("POINT", srid=4326)))
    address_text: str

    status: GigStatus = Field(default=GigStatus.PENDING, index=True)

    # Images for the gig
    image_urls: Optional[List[str]] = Field(default=None, sa_column=Column(JSON))

    created_at: datetime = Field(default_factory=datetime.utcnow, index=True)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    starts_at: Optional[datetime] = None  # When gig should start
    completed_at: Optional[datetime] = None

    # Foreign Keys
    seeker_id: UUID = Field(foreign_key="user.id", index=True)  # User who posted the gig
    helper_id: Optional[UUID] = Field(
        default=None, foreign_key="user.id", index=True
    )  # User who accepted

    # Relationships
    seeker: User = Relationship(
        back_populates="gigs_created",
        sa_relationship_kwargs={"foreign_keys": "Gig.seeker_id"},
    )
    helper: Optional[User] = Relationship(
        back_populates="gigs_accepted",
        sa_relationship_kwargs={"foreign_keys": "Gig.helper_id"},
    )
    chat_room: Optional["ChatRoom"] = Relationship(back_populates="gig")
    reviews: List["Review"] = Relationship(back_populates="gig")
    transaction: Optional["Transaction"] = Relationship(back_populates="gig")


class ChatRoom(SQLModel, table=True):
    """Chat rooms created when gigs are accepted"""

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    is_active: bool = Field(default=True)

    # Foreign Keys
    gig_id: UUID = Field(foreign_key="gig.id", unique=True, index=True)

    # Relationships
    gig: Gig = Relationship(back_populates="chat_room")
    participants: List["ChatParticipant"] = Relationship(back_populates="chat_room")
    messages: List["Message"] = Relationship(back_populates="chat_room")


class ChatParticipant(SQLModel, table=True):
    """Users participating in a chat room"""

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    joined_at: datetime = Field(default_factory=datetime.utcnow)
    last_read_at: Optional[datetime] = None

    # Foreign Keys
    chat_room_id: UUID = Field(foreign_key="chatroom.id", index=True)
    user_id: UUID = Field(foreign_key="user.id", index=True)

    # Relationships
    chat_room: ChatRoom = Relationship(back_populates="participants")
    user: User = Relationship(back_populates="chat_participants")


class Message(SQLModel, table=True):
    """Messages within chat rooms"""

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    content: str
    message_type: MessageType = Field(default=MessageType.TEXT)
    image_url: Optional[str] = None
    is_read: bool = Field(default=False, index=True)
    timestamp: datetime = Field(default_factory=datetime.utcnow, index=True)

    # Foreign Keys
    chat_room_id: UUID = Field(foreign_key="chatroom.id", index=True)
    sender_id: UUID = Field(foreign_key="user.id", index=True)

    # Relationships
    chat_room: ChatRoom = Relationship(back_populates="messages")
    sender: User = Relationship(back_populates="messages_sent")


class BuddyList(SQLModel, table=True):
    """Favorite helpers/seekers (buddy system)"""

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    notes: Optional[str] = None  # Optional notes about the buddy

    # Foreign Keys
    user_id: UUID = Field(foreign_key="user.id", index=True)
    buddy_id: UUID = Field(foreign_key="user.id", index=True)

    # Relationships
    user: User = Relationship(
        back_populates="buddies",
        sa_relationship_kwargs={"foreign_keys": "BuddyList.user_id"},
    )
    buddy: User = Relationship(
        back_populates="buddy_of",
        sa_relationship_kwargs={"foreign_keys": "BuddyList.buddy_id"},
    )


class Review(SQLModel, table=True):
    """Reviews and ratings after gig completion"""

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    rating: int = Field(ge=1, le=5)
    comment: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)

    # Foreign Keys
    gig_id: UUID = Field(foreign_key="gig.id", index=True)
    reviewer_id: UUID = Field(foreign_key="user.id")  # Who wrote the review
    reviewee_id: UUID = Field(foreign_key="user.id")  # Who is being reviewed

    # Relationships
    gig: Gig = Relationship(back_populates="reviews")
    reviewer: User = Relationship(
        back_populates="reviews_written",
        sa_relationship_kwargs={"foreign_keys": "Review.reviewer_id"},
    )
    reviewee: User = Relationship(
        back_populates="reviews_received",
        sa_relationship_kwargs={"foreign_keys": "Review.reviewee_id"},
    )


class Transaction(SQLModel, table=True):
    """Mock payment transactions for gigs"""

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    amount: float  # Total amount
    service_fee: float  # Platform service fee
    net_amount: float  # Amount after service fee
    currency: str = Field(default="THB")
    status: TransactionStatus = Field(default=TransactionStatus.PENDING, index=True)

    created_at: datetime = Field(default_factory=datetime.utcnow)
    completed_at: Optional[datetime] = None

    # Mock payment details
    payment_method: Optional[str] = None
    transaction_ref: Optional[str] = None

    # Foreign Keys
    gig_id: UUID = Field(foreign_key="gig.id", unique=True, index=True)
    payer_id: UUID = Field(foreign_key="user.id", index=True)  # Seeker
    payee_id: UUID = Field(foreign_key="user.id", index=True)  # Helper

    # Relationships
    gig: Gig = Relationship(back_populates="transaction")
    payer: User = Relationship(
        back_populates="transactions_as_payer",
        sa_relationship_kwargs={"foreign_keys": "Transaction.payer_id"},
    )
    payee: User = Relationship(
        back_populates="transactions_as_payee",
        sa_relationship_kwargs={"foreign_keys": "Transaction.payee_id"},
    )


class UploadedFile(SQLModel, table=True):
    """File upload tracking and metadata"""

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    filename: str = Field(index=True)  # Generated filename
    original_filename: str  # User's original filename
    file_path: str  # Server file path
    file_size: int  # File size in bytes
    content_type: str  # MIME type
    upload_category: str = Field(index=True)  # 'profile', 'gig', etc.
    uploaded_at: datetime = Field(default_factory=datetime.utcnow, index=True)
    is_active: bool = Field(default=True, index=True)

    # Foreign Keys
    uploaded_by: UUID = Field(foreign_key="user.id", index=True)

    # Relationships
    uploader: User = Relationship(back_populates="uploaded_files")


# === Enhanced Security Models ===


class UserSession(SQLModel, table=True):
    """
    🔐 Track active user sessions for enhanced security.
    Enables token rotation and session management.
    """
    
    id: str = Field(default_factory=lambda: str(uuid4()), primary_key=True)
    user_id: str = Field(index=True)  # References User.id
    refresh_token_jti: str = Field(unique=True)  # JWT ID for refresh token
    device_info: Optional[str] = None  # User agent, device type
    ip_address: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    last_used: datetime = Field(default_factory=datetime.utcnow)
    expires_at: datetime  # Required - when session expires
    is_active: bool = Field(default=True)
    
    # Optional security features
    login_location: Optional[str] = None  # City/Country
    is_suspicious: bool = Field(default=False)


class BlacklistedToken(SQLModel, table=True):
    """
    🚫 Store blacklisted/revoked tokens for immediate invalidation.
    Critical for logout and security breaches.
    """
    
    jti: str = Field(primary_key=True)  # JWT ID
    token_type: str  # 'access' or 'refresh'
    user_id: str = Field(index=True)  # References User.id
    blacklisted_at: datetime = Field(default_factory=datetime.utcnow)
    reason: Optional[str] = None  # 'logout', 'security_breach', 'expired'
    expires_at: datetime  # When to clean up this record
