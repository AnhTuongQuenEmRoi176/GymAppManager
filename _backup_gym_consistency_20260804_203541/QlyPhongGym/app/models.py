"""SQLAlchemy models shared by the Windows application.

This file intentionally mirrors the columns used by the FastAPI backend and the
`gym_db_full_api.sql` schema. Keeping both ORM layers aligned prevents Windows
writes from producing partial rows that the mobile API cannot read.
"""

from datetime import datetime
from decimal import Decimal

from sqlalchemy import (
    BigInteger,
    Boolean,
    Column,
    Date,
    DateTime,
    DECIMAL,
    Enum,
    ForeignKey,
    Integer,
    JSON,
    String,
    Text,
    Time,
)
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()


def _now() -> datetime:
    return datetime.now()


class Role(Base):
    __tablename__ = "roles"

    id = Column(Integer, primary_key=True)
    name = Column(String(50), unique=True, nullable=False)
    display_name = Column(String(100), nullable=True)
    description = Column(String(255), nullable=True)
    created_at = Column(DateTime, nullable=False, default=_now)


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    username = Column(String(100), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    full_name = Column(String(200))
    phone = Column(String(20))
    email = Column(String(150))
    role_id = Column(Integer, ForeignKey("roles.id"))
    avatar = Column(String(500))
    is_active = Column(Boolean, nullable=False, default=True)
    must_change_password = Column(Boolean, nullable=False, default=False)
    last_login_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, nullable=False, default=_now)
    updated_at = Column(DateTime, nullable=False, default=_now, onupdate=_now)

    role = relationship("Role")


class Receptionist(Base):
    __tablename__ = "receptionists"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True, nullable=False)
    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=True)
    base_salary = Column(DECIMAL(12, 2), nullable=False, default=0)
    note = Column(String(500), nullable=True)
    created_at = Column(DateTime, nullable=False, default=_now)
    updated_at = Column(DateTime, nullable=False, default=_now, onupdate=_now)

    user = relationship("User")


class Trainer(Base):
    __tablename__ = "trainers"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True, nullable=False)
    specialty = Column(String(200))
    start_date = Column(Date)
    end_date = Column(Date, nullable=True)
    base_salary = Column(DECIMAL(12, 2), nullable=False, default=0)
    session_commission_percent = Column(DECIMAL(5, 2), nullable=False, default=Decimal("0.50"))
    bio = Column(Text, nullable=True)
    created_at = Column(DateTime, nullable=False, default=_now)
    updated_at = Column(DateTime, nullable=False, default=_now, onupdate=_now)

    user = relationship("User")


class Member(Base):
    __tablename__ = "members"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True, nullable=False)
    dob = Column(Date, nullable=True)
    gender = Column(Enum("Nam", "Nữ", "Khác"), nullable=True)
    address = Column(String(255))
    emergency_contact_name = Column(String(200), nullable=True)
    emergency_contact_phone = Column(String(20), nullable=True)
    joined_at = Column(DateTime, nullable=False, default=_now)
    status = Column(Enum("active", "inactive", "suspended"), nullable=False, default="active")
    note = Column(Text, nullable=True)
    created_at = Column(DateTime, nullable=False, default=_now)
    updated_at = Column(DateTime, nullable=False, default=_now, onupdate=_now)

    user = relationship("User")


class Package(Base):
    __tablename__ = "packages"

    id = Column(Integer, primary_key=True)
    name = Column(String(150), nullable=False)
    package_type = Column(String(20), nullable=False, default="GYM")
    description = Column(Text, nullable=True)
    price = Column(DECIMAL(12, 2), nullable=False)
    duration_days = Column(Integer, nullable=False)
    sessions = Column(Integer, nullable=True)
    is_active = Column(Boolean, nullable=False, default=True)
    created_at = Column(DateTime, nullable=False, default=_now)
    updated_at = Column(DateTime, nullable=False, default=_now, onupdate=_now)


class MemberPackage(Base):
    __tablename__ = "member_packages"

    id = Column(Integer, primary_key=True)
    member_id = Column(Integer, ForeignKey("members.id"), nullable=False)
    package_id = Column(Integer, ForeignKey("packages.id"), nullable=False)
    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=False)
    sessions_total = Column(Integer, nullable=True)
    sessions_remaining = Column(Integer, nullable=True)
    pt_id = Column(Integer, ForeignKey("trainers.id"), nullable=True)
    pt_session_unit_price = Column(DECIMAL(12, 2), nullable=True)
    price_paid = Column(DECIMAL(12, 2), nullable=False, default=0)
    status = Column(String(20), nullable=False, default="active")
    created_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    created_at = Column(DateTime, nullable=False, default=_now)
    updated_at = Column(DateTime, nullable=False, default=_now, onupdate=_now)

    member = relationship("Member")
    package = relationship("Package")
    trainer = relationship("Trainer")


class MembershipRequest(Base):
    __tablename__ = "membership_requests"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    member_id = Column(Integer, ForeignKey("members.id"), nullable=False)
    request_type = Column(String(30), nullable=False)
    requested_package_id = Column(Integer, ForeignKey("packages.id"), nullable=True)
    requested_trainer_id = Column(Integer, ForeignKey("trainers.id"), nullable=True)
    note = Column(Text, nullable=True)
    status = Column(String(20), nullable=False, default="pending")
    reviewed_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    reviewed_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, nullable=False, default=_now)


class TrainingSchedule(Base):
    __tablename__ = "training_schedules"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    trainer_id = Column(Integer, ForeignKey("trainers.id"), nullable=False)
    member_id = Column(Integer, ForeignKey("members.id"), nullable=False)
    member_package_id = Column(Integer, ForeignKey("member_packages.id"), nullable=True)
    title = Column(String(200), nullable=False)
    start_at = Column(DateTime, nullable=False)
    end_at = Column(DateTime, nullable=False)
    location = Column(String(200), nullable=True)
    note = Column(Text, nullable=True)
    status = Column(String(20), nullable=False, default="upcoming")
    created_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    cancelled_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    cancelled_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, nullable=False, default=_now)
    updated_at = Column(DateTime, nullable=False, default=_now, onupdate=_now)

    trainer = relationship("Trainer")
    member = relationship("Member")
    member_package = relationship("MemberPackage")


class TrainerAvailability(Base):
    __tablename__ = "trainer_availability"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    trainer_id = Column(Integer, ForeignKey("trainers.id"), nullable=False)
    available_date = Column(Date, nullable=False)
    start_time = Column(Time, nullable=False)
    end_time = Column(Time, nullable=False)
    status = Column(String(20), nullable=False, default="available")
    note = Column(String(500), nullable=True)
    created_at = Column(DateTime, nullable=False, default=_now)


class QRDemo(Base):
    __tablename__ = "qr_demo"

    id = Column(Integer, primary_key=True)
    code = Column(String(255), unique=True, nullable=False)
    entity_type = Column(Enum("member", "trainer"), nullable=False)
    entity_id = Column(Integer, nullable=False)
    generated_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    created_at = Column(DateTime, nullable=False, default=_now)


class QRToken(Base):
    __tablename__ = "qr_tokens"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    token_id = Column(String(36), unique=True, nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    entity_type = Column(String(20), nullable=False)
    entity_id = Column(Integer, nullable=False)
    token_hash = Column(String(255), unique=True, nullable=False)
    expires_at = Column(DateTime, nullable=False)
    used_at = Column(DateTime, nullable=True)
    used_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    created_at = Column(DateTime, nullable=False, default=_now)


class Checkin(Base):
    __tablename__ = "checkins"

    id = Column(Integer, primary_key=True)
    member_id = Column(Integer, ForeignKey("members.id"), nullable=True)
    trainer_id = Column(Integer, ForeignKey("trainers.id"), nullable=True)
    scanned_at = Column(DateTime, nullable=False, default=_now)
    scanner_user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    source = Column(String(50), nullable=True)
    qr_payload = Column(String(500), nullable=True)
    photo = Column(String(500), nullable=True)
    status = Column(String(20), nullable=False, default="confirmed")
    confirmed_at = Column(DateTime, nullable=True)
    pair_group_id = Column(String(36), nullable=True)
    idempotency_key = Column(String(100), unique=True, nullable=True)
    device_id = Column(String(150), nullable=True)
    location = Column(String(200), nullable=True)
    note = Column(String(500), nullable=True)

    member = relationship("Member")
    trainer = relationship("Trainer")


class PTSession(Base):
    __tablename__ = "pt_sessions"

    id = Column(Integer, primary_key=True)
    trainer_id = Column(Integer, ForeignKey("trainers.id"), nullable=False)
    member_id = Column(Integer, ForeignKey("members.id"), nullable=False)
    member_package_id = Column(Integer, ForeignKey("member_packages.id"), nullable=True)
    schedule_id = Column(BigInteger, ForeignKey("training_schedules.id"), nullable=True)
    session_date = Column(DateTime, nullable=False, default=_now)
    confirmed_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    status = Column(String(20), nullable=False, default="confirmed")
    commission_rate = Column(DECIMAL(5, 2), nullable=False, default=Decimal("0.50"))
    commission_amount = Column(DECIMAL(12, 2), nullable=False, default=0)
    note = Column(String(500), nullable=True)
    created_at = Column(DateTime, nullable=False, default=_now)


class Transaction(Base):
    __tablename__ = "transactions"

    id = Column(Integer, primary_key=True)
    type = Column(String(20), nullable=False)
    amount = Column(DECIMAL(12, 2), nullable=False, default=0)
    date = Column(DateTime, nullable=False, default=_now)
    description = Column(Text, nullable=True)
    created_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    reference_type = Column(String(50), nullable=True)
    reference_id = Column(BigInteger, nullable=True)


class Payment(Base):
    __tablename__ = "payments"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    payment_code = Column(String(50), unique=True, nullable=False)
    member_id = Column(Integer, ForeignKey("members.id"), nullable=True)
    member_package_id = Column(Integer, ForeignKey("member_packages.id"), nullable=True)
    amount = Column(DECIMAL(12, 2), nullable=False)
    method = Column(String(30), nullable=False, default="cash")
    status = Column(String(20), nullable=False, default="paid")
    paid_at = Column(DateTime, nullable=True)
    confirmed_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    note = Column(String(500), nullable=True)
    created_at = Column(DateTime, nullable=False, default=_now)


class Notification(Base):
    __tablename__ = "notifications"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    type = Column(String(50), nullable=False)
    title = Column(String(200), nullable=False)
    body = Column(Text, nullable=False)
    data_json = Column(JSON, nullable=True)
    is_read = Column(Boolean, nullable=False, default=False)
    read_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, nullable=False, default=_now)
