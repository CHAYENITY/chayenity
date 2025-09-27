import enum
from typing import Optional, List
from datetime import datetime
from uuid import UUID, uuid4

from sqlalchemy import Column, text as sa_text
from sqlalchemy import JSON
from sqlmodel import SQLModel, Field, Relationship

from app.database.base import Base


# === Enum Definitions ===


class ItemStatus(str, enum.Enum):
    AVAILABLE = "available"
    RESERVED = "reserved"
    SOLD = "sold"


class ItemCondition(str, enum.Enum):
    NEW = "new"
    USED_LIKE_NEW = "used_like_new"
    USED_GOOD = "used_good"
    USED_FAIR = "used_fair"


class ReportType(str, enum.Enum):
    SPAM = "spam"
    INAPPROPRIATE = "inappropriate"
    SCAM = "scam"
    FAKE_ITEM = "fake_item"
    OTHER = "other"


class NotificationType(str, enum.Enum):
    NEW_MESSAGE = "new_message"
    ITEM_INTEREST = "item_interest"
    PRICE_CHANGE = "price_change"
    REVIEW_RECEIVED = "review_received"
    REPORT_RESPONSE = "report_response"
class TransactionStatus(str, enum.Enum):
    PENDING = "pending"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    FAILED = "failed"


# === Core Entities ===


class User(SQLModel, table=True):
    """User accounts for the marketplace"""

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    email: str = Field(unique=True, index=True)
    hashed_password: str
    full_name: str
    profile_image_url: Optional[str] = None
    contact_info: Optional[str] = None  # phone or LINE ID
    address_text: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    is_verified: bool = Field(default=False)
    reputation_score: float = Field(default=5.0)
    created_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationships
    items: List["Item"] = Relationship(back_populates="owner")
    reviews_written: List["Review"] = Relationship(
        back_populates="reviewer", sa_relationship_kwargs={"foreign_keys": "Review.reviewer_id"}
    )
    reviews_received: List["Review"] = Relationship(
        back_populates="reviewee", sa_relationship_kwargs={"foreign_keys": "Review.reviewee_id"}
    )
    favorites: List["Favorite"] = Relationship(back_populates="user")
    notifications: List["Notification"] = Relationship(back_populates="user")
    reports_as_reporter: List["Report"] = Relationship(
        back_populates="reporter", sa_relationship_kwargs={"foreign_keys": "Report.reporter_id"}
    )
    reports_as_reported: List["Report"] = Relationship(
        back_populates="reported_user",
        sa_relationship_kwargs={"foreign_keys": "Report.reported_user_id"},
    )
    wanted_items: List["WantedItem"] = Relationship(back_populates="user")
    transactions_as_buyer: List["Transaction"] = Relationship(
        back_populates="buyer", sa_relationship_kwargs={"foreign_keys": "Transaction.buyer_id"}
    )
    transactions_as_seller: List["Transaction"] = Relationship(
        back_populates="seller", sa_relationship_kwargs={"foreign_keys": "Transaction.seller_id"}
    )


class Category(SQLModel, table=True):
    """Item categories for marketplace"""

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    name: str = Field(unique=True, index=True)

    # Relationships
    items: List["Item"] = Relationship(back_populates="category")


class Item(SQLModel, table=True):
    """Items for sale in the marketplace"""

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    title: str = Field(index=True)
    description: str
    price: float = Field(index=True)
    condition: ItemCondition
    status: ItemStatus = Field(default=ItemStatus.AVAILABLE, index=True)
    latitude: float
    longitude: float
    created_at: datetime = Field(default_factory=datetime.utcnow, index=True)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    # Foreign Keys
    category_id: UUID = Field(foreign_key="category.id", index=True)
    owner_id: UUID = Field(foreign_key="user.id", index=True)

    # Relationships
    owner: User = Relationship(back_populates="items")
    category: Category = Relationship(back_populates="items")
    images: List["ItemImage"] = Relationship(back_populates="item")
    reviews: List["Review"] = Relationship(back_populates="item")
    favorited_by: List["Favorite"] = Relationship(back_populates="item")
    conversations: List["Conversation"] = Relationship(back_populates="item")
    transactions: List["Transaction"] = Relationship(back_populates="item")


class ItemImage(SQLModel, table=True):
    """Images for marketplace items"""

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    image_url: str
    item_id: UUID = Field(foreign_key="item.id")

    # Relationships
    item: Item = Relationship(back_populates="images")


# === Social Features ===


class Review(SQLModel, table=True):
    """Reviews and ratings for users and items"""

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    rating: int = Field(ge=1, le=5)
    comment: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)

    # Foreign Keys
    reviewer_id: UUID = Field(foreign_key="user.id")
    reviewee_id: UUID = Field(foreign_key="user.id")
    item_id: UUID = Field(foreign_key="item.id")

    # Relationships
    reviewer: User = Relationship(
        back_populates="reviews_written",
        sa_relationship_kwargs={"foreign_keys": "Review.reviewer_id"},
    )
    reviewee: User = Relationship(
        back_populates="reviews_received",
        sa_relationship_kwargs={"foreign_keys": "Review.reviewee_id"},
    )
    item: Item = Relationship(back_populates="reviews")


class Favorite(SQLModel, table=True):
    """User's favorite items"""

    user_id: UUID = Field(foreign_key="user.id", primary_key=True)
    item_id: UUID = Field(foreign_key="item.id", primary_key=True)

    # Relationships
    user: User = Relationship(back_populates="favorites")
    item: Item = Relationship(back_populates="favorited_by")


class WantedItem(SQLModel, table=True):
    """Items that users want to buy (wishlist)"""

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    user_id: UUID = Field(foreign_key="user.id")
    title: str
    description: Optional[str] = None
    category_id: Optional[UUID] = Field(default=None, foreign_key="category.id")
    max_price: Optional[float] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationships
    user: User = Relationship(back_populates="wanted_items")
    category: Optional[Category] = Relationship()


# === Communication ===


class Conversation(SQLModel, table=True):
    """Chat conversations between users about items"""

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    item_id: UUID = Field(foreign_key="item.id")
    user1_id: UUID = Field(foreign_key="user.id")
    user2_id: UUID = Field(foreign_key="user.id")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationships
    messages: List["Message"] = Relationship(back_populates="conversation")
    item: Item = Relationship(back_populates="conversations")
    user1: User = Relationship(sa_relationship_kwargs={"foreign_keys": "Conversation.user1_id"})
    user2: User = Relationship(sa_relationship_kwargs={"foreign_keys": "Conversation.user2_id"})


class Message(SQLModel, table=True):
    """Messages within conversations"""

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    content: str
    image_url: Optional[str] = None
    is_read: bool = Field(default=False, index=True)
    is_unsent: bool = Field(default=False)
    timestamp: datetime = Field(default_factory=datetime.utcnow, index=True)

    # Foreign Keys
    conversation_id: UUID = Field(foreign_key="conversation.id", index=True)
    sender_id: UUID = Field(foreign_key="user.id", index=True)

    # Relationships
    conversation: Conversation = Relationship(back_populates="messages")
    sender: User = Relationship()


# === System Features ===


class Report(SQLModel, table=True):
    """User reports for inappropriate behavior"""

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    reporter_id: UUID = Field(foreign_key="user.id")
    reported_user_id: UUID = Field(foreign_key="user.id")
    reason: ReportType
    description: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationships
    reporter: User = Relationship(
        back_populates="reports_as_reporter",
        sa_relationship_kwargs={"foreign_keys": "Report.reporter_id"},
    )
    reported_user: User = Relationship(
        back_populates="reports_as_reported",
        sa_relationship_kwargs={"foreign_keys": "Report.reported_user_id"},
    )


class Notification(SQLModel, table=True):
    """Push notifications for users"""

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    user_id: UUID = Field(foreign_key="user.id", index=True)
    title: str
    message: str
    type: NotificationType = Field(index=True)
    is_read: bool = Field(default=False, index=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    extra_data: Optional[dict] = Field(
        default=None, sa_column=Column(JSON, server_default=sa_text("'{}'"))
    )  # e.g., {"item_id": "...", "sender_id": "...", "conversation_id": "..."}

    # Relationships
    user: User = Relationship(back_populates="notifications")


class Transaction(SQLModel, table=True):
    """Transaction records for completed sales"""

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    item_id: UUID = Field(foreign_key="item.id", index=True)
    buyer_id: UUID = Field(foreign_key="user.id", index=True)
    seller_id: UUID = Field(foreign_key="user.id", index=True)
    amount: float  # Price at time of transaction (in case of negotiation)
    currency: str = Field(default="THB")
    status: TransactionStatus = Field(default=TransactionStatus.PENDING, index=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    completed_at: Optional[datetime] = None
    deleted_at: Optional[datetime] = None

    # Relationships
    item: Item = Relationship(back_populates="transactions")
    buyer: User = Relationship(
        back_populates="transactions_as_buyer",
        sa_relationship_kwargs={"foreign_keys": "Transaction.buyer_id"},
    )
    seller: User = Relationship(
        back_populates="transactions_as_seller",
        sa_relationship_kwargs={"foreign_keys": "Transaction.seller_id"},
    )
