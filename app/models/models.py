from sqlalchemy import (
    Column, String, Float, Text, Enum, Boolean, ForeignKey,
    Integer, DateTime, CHAR, Table, JSON
)
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid
import enum
from sqlalchemy import Enum as SqlEnum
from app.database import Base

# ============================================================
# ENUM DEFINITIONS
# ============================================================

class RoleEnum(str, enum.Enum):
    user = "user"
    admin = "admin"
    store = "store"

class PaymentStatusEnum(str, enum.Enum):
    pending = "pending"
    paid = "paid"
    failed = "failed"

class PaymentMethodEnum(str, enum.Enum):
    credit_card = "credit_card"
    debit_card = "debit_card"
    net_banking = "net_banking"
    upi = "upi"
    cod = "cod"


# ============================================================
# FOLLOWERS ASSOCIATION TABLE
# ============================================================

followers_association = Table(
    "user_followers",
    Base.metadata,
    Column("follower_id", String(36), ForeignKey("users.id"), primary_key=True),
    Column("followed_id", String(36), ForeignKey("users.id"), primary_key=True),
    Column("created_at", DateTime, default=datetime.utcnow)
)


# ============================================================
# USER MODEL
# ============================================================

class User(Base):
    __tablename__ = "users"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String(100), nullable=False)
    email = Column(String(255), unique=True, nullable=False)
    username = Column(String(100), unique=True, nullable=False)
    passwordHash = Column(String(255), nullable=False)
    role = Column(SqlEnum(RoleEnum, native_enum=False), nullable=False, default=RoleEnum.user)

    profileImage = Column(String(255), nullable=True)
    profileImagePublicId = Column(String(255), nullable=True)

    createdAt = Column(DateTime, default=datetime.utcnow)
    updatedAt = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    location = Column(String(100), nullable=True)
    pincode = Column(CHAR(6), nullable=True)
    gender = Column(String(20), nullable=True)
    age = Column(Integer, nullable=True)
    phone = Column(String(15), nullable=True)
    bio = Column(String(500), nullable=True)
    profile_completion = Column(Integer, default=0)

    isActive = Column(Boolean, default=False)
    isAgreedtoTC = Column(Boolean, default=False)

    # Relationships
    artworks = relationship("Artwork", back_populates="artist")
    orders = relationship("Order", back_populates="buyer")
    reviews = relationship("Review", back_populates="reviewer", foreign_keys="Review.reviewerId")
    Saved_items = relationship("Saved", back_populates="user")
    cart_items = relationship("Cart", back_populates="user")
    liked_artworks = relationship("ArtworkLike", back_populates="user", cascade="all, delete-orphan")
    comments = relationship("Comment", back_populates="user", cascade="all, delete-orphan")

    followers = relationship(
        "User",
        secondary=followers_association,
        primaryjoin=id == followers_association.c.followed_id,
        secondaryjoin=id == followers_association.c.follower_id,
        backref="following",
    )


# ============================================================
# ARTWORKS
# ============================================================

class Artwork(Base):
    __tablename__ = "artworks"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    title = Column(String(200), nullable=False)
    description = Column(Text)
    price = Column(Float, nullable=True)
    quantity = Column(Integer, nullable=True, default=None)
    tags = Column(JSON, default=list)

    category = Column(String(100), nullable=False)
    artistId = Column(String(36), ForeignKey("users.id"))

    createdAt = Column(DateTime, default=datetime.utcnow)

    isSold = Column(Boolean, default=False)
    isDeleted = Column(Boolean, default=False)
    forSale = Column(Boolean, default=False)

    artist = relationship("User", back_populates="artworks")
    images = relationship("ArtworkImage", back_populates="artwork", cascade="all, delete-orphan")
    orders = relationship("Order", back_populates="artwork")
    reviews = relationship("Review", back_populates="artwork")
    Saved_items = relationship("Saved", back_populates="artwork")
    cart_items = relationship("Cart", back_populates="artwork")
    likes = relationship("ArtworkLike", back_populates="artwork", cascade="all, delete-orphan")
    comments = relationship("Comment", back_populates="artwork", cascade="all, delete-orphan")


class ArtworkImage(Base):
    __tablename__ = "artwork_images"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    artwork_id = Column(String(36), ForeignKey("artworks.id"))
    url = Column(String(500), nullable=False)
    public_id = Column(String(255), nullable=False)

    artwork = relationship("Artwork", back_populates="images")


class ArtworkLike(Base):
    __tablename__ = "artwork_likes"

    userId = Column(String(36), ForeignKey("users.id"), primary_key=True)
    artworkId = Column(String(36), ForeignKey("artworks.id"), primary_key=True)
    createdAt = Column(DateTime, default=datetime.utcnow)

    artwork = relationship("Artwork", back_populates="likes")
    user = relationship("User", back_populates="liked_artworks")


class Comment(Base):
    __tablename__ = "comments"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(36), ForeignKey("users.id"))
    artwork_id = Column(String(36), ForeignKey("artworks.id"))
    content = Column(String(500), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="comments")
    artwork = relationship("Artwork", back_populates="comments")


# ============================================================
# ORDERS & PAYMENTS
# ============================================================

class Order(Base):
    __tablename__ = "orders"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    buyerId = Column(String(36), ForeignKey("users.id"))
    artworkId = Column(String(36), ForeignKey("artworks.id"))
    totalAmount = Column(Float, nullable=False)
    paymentStatus = Column(SqlEnum(PaymentStatusEnum, native_enum=False))
    createdAt = Column(DateTime, default=datetime.utcnow)

    buyer = relationship("User", back_populates="orders")
    artwork = relationship("Artwork", back_populates="orders")


class Payment(Base):
    __tablename__ = "payments"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    order_id = Column(String(36), ForeignKey("orders.id"), nullable=False)
    user_id = Column(String(36), ForeignKey("users.id"), nullable=False)
    transaction_id = Column(String(100), unique=True)
    amount = Column(Float, nullable=False)
    status = Column(SqlEnum(PaymentStatusEnum, native_enum=False), default=PaymentStatusEnum.pending)
    method = Column(SqlEnum(PaymentMethodEnum, native_enum=False))
    paid_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", backref="payments")
    order = relationship("Order", backref="payment")


# ============================================================
# REVIEWS
# ============================================================

class Review(Base):
    __tablename__ = "reviews"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    reviewerId = Column(String(36), ForeignKey("users.id"))
    artistId = Column(String(36), ForeignKey("users.id"))
    artworkId = Column(String(36), ForeignKey("artworks.id"))
    rating = Column(Integer, nullable=False)
    comment = Column(Text)
    createdAt = Column(DateTime, default=datetime.utcnow)

    reviewer = relationship("User", back_populates="reviews", foreign_keys=[reviewerId])
    artwork = relationship("Artwork", back_populates="reviews")
    artist = relationship("User", foreign_keys=[artistId])


# class ArtistReview(Base):
#     __tablename__ = "artist_reviews"

#     id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
#     reviewer_id = Column(String(36), ForeignKey("users.id"))
#     artist_id = Column(String(36), ForeignKey("users.id"))
#     rating = Column(Integer, nullable=False)
#     comment = Column(Text)
#     created_at = Column(DateTime, default=datetime.utcnow)

#     reviewer = relationship("User", foreign_keys=[reviewer_id], backref="artist_reviews_made")
#     artist = relationship("User", foreign_keys=[artist_id], backref="artist_reviews_received")


# ============================================================
# SAVED & CART
# ============================================================

# class Saved(Base):
#     __tablename__ = "saved"

#     id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
#     userId = Column(String(36), ForeignKey("users.id"))
#     artworkId = Column(String(36), ForeignKey("artworks.id"))
#     createdAt = Column(DateTime, default=datetime.utcnow)

#     user = relationship("User", back_populates="Saved_items")
#     artwork = relationship("Artwork", back_populates="Saved_items")


# class Cart(Base):
#     __tablename__ = "cart"

#     id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
#     userId = Column(String(36), ForeignKey("users.id"))
#     artworkId = Column(String(36), ForeignKey("artworks.id"))
#     purchase_quantity = Column(Integer, default=1)
#     createdAt = Column(DateTime, default=datetime.utcnow)

#     user = relationship("User", back_populates="cart_items")
#     artwork = relationship("Artwork", back_populates="cart_items")


# ============================================================
# MESSAGES
# ============================================================

class Message(Base):
    __tablename__ = "messages"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    sender_id = Column(String(36), ForeignKey("users.id"))
    receiver_id = Column(String(36), ForeignKey("users.id"))
    content = Column(Text)
    timestamp = Column(DateTime, nullable=False)
    is_read = Column(Boolean, default=False)
    message_type = Column(String(20), default="text")

    sender = relationship("User", foreign_keys=[sender_id])
    receiver = relationship("User", foreign_keys=[receiver_id])


# ============================================================
# ADMIN AUDIT LOG
# ============================================================

class AdminAuditLog(Base):
    __tablename__ = "admin_audit_logs"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    admin_id = Column(String(36), ForeignKey("users.id"))
    method = Column(String(10))
    path = Column(String(255))
    action = Column(String(100))
    description = Column(Text)
    ip_address = Column(String(50))
    timestamp = Column(DateTime, default=datetime.utcnow)

    admin = relationship("User", backref="admin_logs")


# ============================================================
# OPTIONAL AI SUPPORT TABLES
# ============================================================

class AIFlag(Base):
    __tablename__ = "ai_flags"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(36), ForeignKey("users.id"))
    content_type = Column(String(50))
    content_id = Column(String(36))
    issue = Column(String(255))
    confidence = Column(Float)
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User")


class FraudLog(Base):
    __tablename__ = "fraud_logs"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(36), ForeignKey("users.id"))
    event = Column(String(255))
    risk_score = Column(Float)
    metadata = Column(JSON)
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User")


class BotActivity(Base):
    __tablename__ = "bot_activity"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(36), ForeignKey("users.id"))
    action = Column(String(50))
    details = Column(JSON)
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User")


class Recommendation(Base):
    __tablename__ = "recommendations"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(36), ForeignKey("users.id"))
    artworks = Column(JSON)
    generated_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User")
