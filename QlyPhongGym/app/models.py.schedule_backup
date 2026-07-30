from sqlalchemy import Column, Integer, String, DateTime, Date, ForeignKey, DECIMAL, Text, Enum, Boolean
from sqlalchemy.orm import relationship, declarative_base
from datetime import datetime

Base = declarative_base()


class Role(Base):
    __tablename__ = 'roles'
    id = Column(Integer, primary_key=True)
    name = Column(String(50), unique=True, nullable=False)


class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    username = Column(String(100), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    full_name = Column(String(200))
    phone = Column(String(20))
    email = Column(String(150))
    role_id = Column(Integer, ForeignKey('roles.id'))
    avatar = Column(String(500))
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    role = relationship('Role')


class Trainer(Base):
    __tablename__ = 'trainers'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), unique=True)
    specialty = Column(String(200))
    start_date = Column(Date)
    end_date = Column(Date, nullable=True)
    base_salary = Column(DECIMAL(12,2), default=0.00)

    user = relationship('User')


class Member(Base):
    __tablename__ = 'members'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), unique=True)
    dob = Column(Date, nullable=True)
    gender = Column(Enum('Nam','Nữ','Khác'))
    address = Column(String(255))
    joined_at = Column(DateTime, default=datetime.utcnow)
    status = Column(Enum('active','inactive','suspended'), default='active')

    user = relationship('User')


class Package(Base):
    __tablename__ = 'packages'
    id = Column(Integer, primary_key=True)
    name = Column(String(150))
    price = Column(DECIMAL(12,2), nullable=False)
    duration_days = Column(Integer, nullable=False)
    sessions = Column(Integer, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)


class MemberPackage(Base):
    __tablename__ = 'member_packages'
    id = Column(Integer, primary_key=True)
    member_id = Column(Integer, ForeignKey('members.id'))
    package_id = Column(Integer, ForeignKey('packages.id'))
    start_date = Column(Date)
    end_date = Column(Date)
    sessions_remaining = Column(Integer, nullable=True)
    pt_id = Column(Integer, ForeignKey('trainers.id'), nullable=True)
    price_paid = Column(DECIMAL(12,2))
    created_at = Column(DateTime, default=datetime.utcnow)

    member = relationship('Member')
    package = relationship('Package')


class Checkin(Base):
    __tablename__ = 'checkins'
    id = Column(Integer, primary_key=True)
    member_id = Column(Integer, ForeignKey('members.id'), nullable=True)
    trainer_id = Column(Integer, ForeignKey('trainers.id'), nullable=True)
    scanned_at = Column(DateTime, default=datetime.utcnow)
    scanner_user_id = Column(Integer, ForeignKey('users.id'), nullable=True)
    source = Column(String(50))
    qr_payload = Column(String(500))
    photo = Column(String(500), nullable=True)

    member = relationship('Member')
    trainer = relationship('Trainer')


class QRDemo(Base):
    __tablename__ = 'qr_demo'
    id = Column(Integer, primary_key=True)
    code = Column(String(255), unique=True)
    entity_type = Column(Enum('member','trainer'))
    entity_id = Column(Integer)
    created_at = Column(DateTime, default=datetime.utcnow)


class PTSession(Base):
    __tablename__ = 'pt_sessions'
    id = Column(Integer, primary_key=True)
    trainer_id = Column(Integer, ForeignKey('trainers.id'))
    member_id = Column(Integer, ForeignKey('members.id'))
    session_date = Column(DateTime)
    confirmed_by = Column(Integer, ForeignKey('users.id'))
    created_at = Column(DateTime, default=datetime.utcnow)


class Transaction(Base):
    __tablename__ = 'transactions'
    id = Column(Integer, primary_key=True)
    type = Column(Enum('payment','salary','refund','other'))
    amount = Column(DECIMAL(12,2))
    date = Column(DateTime, default=datetime.utcnow)
    description = Column(Text)
    created_by = Column(Integer, ForeignKey('users.id'))
