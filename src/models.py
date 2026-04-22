from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Boolean, Date, Time
from sqlalchemy.orm import relationship
from datetime import datetime
from src.database import Base


# -----------------------------
# INSTITUTION
# -----------------------------
class Institution(Base):
    __tablename__ = "institutions"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    users = relationship("User", back_populates="institution")
    batches = relationship("Batch", back_populates="institution")


# -----------------------------
# USER (ALL ROLES)
# -----------------------------
class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    role = Column(String, nullable=False)  # student, trainer, etc.
    institution_id = Column(Integer, ForeignKey("institutions.id"), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    institution = relationship("Institution", back_populates="users")

    sessions = relationship("Session", back_populates="trainer")
    attendance_records = relationship("Attendance", back_populates="student")


# -----------------------------
# BATCH
# -----------------------------
class Batch(Base):
    __tablename__ = "batches"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    institution_id = Column(Integer, ForeignKey("institutions.id"))
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    institution = relationship("Institution", back_populates="batches")

    sessions = relationship("Session", back_populates="batch")
    invites = relationship("BatchInvite", back_populates="batch")


# -----------------------------
# MANY-TO-MANY: TRAINERS ↔ BATCH
# -----------------------------
class BatchTrainer(Base):
    __tablename__ = "batch_trainers"

    batch_id = Column(Integer, ForeignKey("batches.id"), primary_key=True)
    trainer_id = Column(Integer, ForeignKey("users.id"), primary_key=True)


# -----------------------------
# MANY-TO-MANY: STUDENTS ↔ BATCH
# -----------------------------
class BatchStudent(Base):
    __tablename__ = "batch_students"

    batch_id = Column(Integer, ForeignKey("batches.id"), primary_key=True)
    student_id = Column(Integer, ForeignKey("users.id"), primary_key=True)


# -----------------------------
# BATCH INVITE
# -----------------------------
class BatchInvite(Base):
    __tablename__ = "batch_invites"

    id = Column(Integer, primary_key=True, index=True)
    batch_id = Column(Integer, ForeignKey("batches.id"))
    token = Column(String, unique=True, nullable=False)
    created_by = Column(Integer, ForeignKey("users.id"))
    expires_at = Column(DateTime)
    used = Column(Boolean, default=False)

    # Relationships
    batch = relationship("Batch", back_populates="invites")


# -----------------------------
# SESSION
# -----------------------------
class Session(Base):
    __tablename__ = "sessions"

    id = Column(Integer, primary_key=True, index=True)
    batch_id = Column(Integer, ForeignKey("batches.id"))
    trainer_id = Column(Integer, ForeignKey("users.id"))
    title = Column(String, nullable=False)

    date = Column(Date, nullable=False)
    start_time = Column(Time, nullable=False)
    end_time = Column(Time, nullable=False)

    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    batch = relationship("Batch", back_populates="sessions")
    trainer = relationship("User", back_populates="sessions")
    attendance = relationship("Attendance", back_populates="session")


# -----------------------------
# ATTENDANCE
# -----------------------------
class Attendance(Base):
    __tablename__ = "attendance"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(Integer, ForeignKey("sessions.id"))
    student_id = Column(Integer, ForeignKey("users.id"))

    status = Column(String, nullable=False)  # present / absent / late
    marked_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    session = relationship("Session", back_populates="attendance")
    student = relationship("User", back_populates="attendance_records")