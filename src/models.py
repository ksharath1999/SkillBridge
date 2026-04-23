from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Boolean, Date, Time, UniqueConstraint
from datetime import datetime
from src.database import Base


class Institution(Base):
    __tablename__ = "institutions"

    id = Column(Integer, primary_key=True)
    name = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    name = Column(String)
    email = Column(String, unique=True)
    hashed_password = Column(String)
    role = Column(String)
    institution_id = Column(Integer, ForeignKey("institutions.id"), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)


class Batch(Base):
    __tablename__ = "batches"

    id = Column(Integer, primary_key=True)
    name = Column(String)
    institution_id = Column(Integer, ForeignKey("institutions.id"))
    created_at = Column(DateTime, default=datetime.utcnow)


class BatchStudent(Base):
    __tablename__ = "batch_students"

    batch_id = Column(Integer, ForeignKey("batches.id"), primary_key=True)
    student_id = Column(Integer, ForeignKey("users.id"), primary_key=True)


class BatchInvite(Base):
    __tablename__ = "batch_invites"

    id = Column(Integer, primary_key=True)
    batch_id = Column(Integer, ForeignKey("batches.id"))
    token = Column(String, unique=True)
    created_by = Column(Integer, ForeignKey("users.id"))
    expires_at = Column(DateTime)
    used = Column(Boolean, default=False)


class Session(Base):
    __tablename__ = "sessions"

    id = Column(Integer, primary_key=True)
    batch_id = Column(Integer, ForeignKey("batches.id"))
    trainer_id = Column(Integer, ForeignKey("users.id"))
    title = Column(String)
    date = Column(Date)
    start_time = Column(Time)
    end_time = Column(Time)
    created_at = Column(DateTime, default=datetime.utcnow)


class Attendance(Base):
    __tablename__ = "attendance"

    id = Column(Integer, primary_key=True)
    session_id = Column(Integer, ForeignKey("sessions.id"))
    student_id = Column(Integer, ForeignKey("users.id"))
    status = Column(String)
    marked_at = Column(DateTime, default=datetime.utcnow)

    __table_args__ = (
        UniqueConstraint("session_id", "student_id", name="unique_attendance"),
    )

class BatchTrainer(Base):
    __tablename__ = "batch_trainers"

    batch_id = Column(Integer, ForeignKey("batches.id"), primary_key=True)
    trainer_id = Column(Integer, ForeignKey("users.id"), primary_key=True)