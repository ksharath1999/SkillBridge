from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
import uuid
import os
from dotenv import load_dotenv

from src.database import engine, get_db
from src.models import Base, User, Batch, Session as DBSession, Attendance, BatchInvite, BatchStudent
from src.schemas import UserCreate, UserLogin
from src.auth import (
    hash_password,
    verify_password,
    create_access_token,
    require_roles,
    get_current_user,
    create_monitoring_token
)
from src.monitoring import get_monitoring_user

load_dotenv()

app = FastAPI()

Base.metadata.create_all(bind=engine)

MONITORING_API_KEY = os.getenv("MONITORING_API_KEY", "12345")


# ---------------- ROOT ----------------
@app.get("/")
def root():
    return {"message": "SkillBridge API running 🚀"}


# ---------------- AUTH ----------------
@app.post("/auth/signup")
def signup(user: UserCreate, db: Session = Depends(get_db)):

    existing = db.query(User).filter(User.email == user.email).first()
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")

    new_user = User(
        name=user.name,
        email=user.email,
        hashed_password=hash_password(user.password),
        role=user.role,
        institution_id=user.institution_id
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    token = create_access_token({
        "user_id": new_user.id,
        "role": new_user.role,
        "institution_id": new_user.institution_id
    })

    return {"access_token": token}


@app.post("/auth/login")
def login(user: UserLogin, db: Session = Depends(get_db)):

    db_user = db.query(User).filter(User.email == user.email).first()

    if not db_user or not verify_password(user.password, db_user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    token = create_access_token({
        "user_id": db_user.id,
        "role": db_user.role,
        "institution_id": db_user.institution_id
    })

    return {"access_token": token}


# ---------------- BATCH ----------------
@app.post("/batches")
def create_batch(
    name: str,
    db: Session = Depends(get_db),
    user=Depends(require_roles(["trainer", "institution"]))
):
    batch = Batch(
        name=name,
        institution_id=user.get("institution_id")
    )

    db.add(batch)
    db.commit()
    db.refresh(batch)

    return {"id": batch.id, "name": batch.name}


# ---------------- INVITE ----------------
@app.post("/batches/{batch_id}/invite")
def create_invite(
    batch_id: int,
    db: Session = Depends(get_db),
    user=Depends(require_roles(["trainer"]))
):
    token = str(uuid.uuid4())

    invite = BatchInvite(
        batch_id=batch_id,
        token=token,
        created_by=user["user_id"],
        expires_at=datetime.utcnow() + timedelta(days=1),  # expiry added
        used=False
    )

    db.add(invite)
    db.commit()

    return {"invite_token": token}


# ---------------- JOIN ----------------
@app.post("/batches/join")
def join_batch(
    token: str,
    db: Session = Depends(get_db),
    user=Depends(require_roles(["student"]))
):
    invite = db.query(BatchInvite).filter(BatchInvite.token == token).first()

    if not invite or invite.used:
        raise HTTPException(status_code=400, detail="Invalid or used invite")

    if invite.expires_at < datetime.utcnow():
        raise HTTPException(status_code=400, detail="Invite expired")

    db.add(BatchStudent(
        batch_id=invite.batch_id,
        student_id=user["user_id"]
    ))

    invite.used = True
    db.commit()

    return {"message": "Joined batch"}


# ---------------- SESSION ----------------
@app.post("/sessions")
def create_session(
    batch_id: int,
    title: str,
    db: Session = Depends(get_db),
    user=Depends(require_roles(["trainer"]))
):
    batch = db.query(Batch).filter(Batch.id == batch_id).first()
    if not batch:
        raise HTTPException(status_code=404, detail="Batch not found")

    session = DBSession(
        batch_id=batch_id,
        trainer_id=user["user_id"],
        title=title,
        date=datetime.utcnow().date(),
        start_time=datetime.utcnow().time(),
        end_time=datetime.utcnow().time()
    )

    db.add(session)
    db.commit()
    db.refresh(session)

    return {"id": session.id}


# ---------------- ATTENDANCE ----------------
@app.post("/attendance/mark")
def mark_attendance(
    session_id: int,
    status: str,
    db: Session = Depends(get_db),
    user=Depends(require_roles(["student"]))
):
    session = db.query(DBSession).filter(DBSession.id == session_id).first()

    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    enrolled = db.query(BatchStudent).filter(
        BatchStudent.batch_id == session.batch_id,
        BatchStudent.student_id == user["user_id"]
    ).first()

    if not enrolled:
        raise HTTPException(status_code=403, detail="Not enrolled in this batch")

    # prevent duplicate attendance
    existing = db.query(Attendance).filter(
        Attendance.session_id == session_id,
        Attendance.student_id == user["user_id"]
    ).first()

    if existing:
        raise HTTPException(status_code=400, detail="Already marked")

    attendance = Attendance(
        session_id=session_id,
        student_id=user["user_id"],
        status=status
    )

    db.add(attendance)
    db.commit()

    return {"message": "Attendance marked"}


# ---------------- TRAINER VIEW ----------------
@app.get("/sessions/{session_id}/attendance")
def get_attendance(
    session_id: int,
    db: Session = Depends(get_db),
    user=Depends(require_roles(["trainer"]))
):
    records = db.query(Attendance).filter(Attendance.session_id == session_id).all()
    return records


# ---------------- MONITORING TOKEN ----------------
@app.post("/auth/monitoring-token")
def get_monitoring_token(
    api_key: str,
    user=Depends(get_current_user)
):
    if user["role"] != "monitoring_officer":
        raise HTTPException(status_code=403, detail="Not allowed")

    if api_key != MONITORING_API_KEY:
        raise HTTPException(status_code=401, detail="Invalid API key")

    token = create_monitoring_token({
        "user_id": user["user_id"],
        "role": user["role"]
    })

    return {"monitoring_token": token}


# ---------------- MONITORING ----------------
@app.get("/monitoring/attendance")
def monitoring_attendance(
    db: Session = Depends(get_db),
    user=Depends(get_monitoring_user)
):
    return db.query(Attendance).all()


@app.post("/monitoring/attendance")
def invalid_method():
    raise HTTPException(status_code=405, detail="Method not allowed")


# ---------------- SUMMARY ----------------
@app.get("/batches/{batch_id}/summary")
def batch_summary(
    batch_id: int,
    db: Session = Depends(get_db),
    user=Depends(require_roles(["institution"]))
):
    sessions = db.query(DBSession).filter(DBSession.batch_id == batch_id).all()

    attendance = db.query(Attendance).join(DBSession).filter(
        DBSession.batch_id == batch_id
    ).all()

    return {
        "total_sessions": len(sessions),
        "attendance_records": len(attendance)
    }


@app.get("/institutions/{inst_id}/summary")
def institution_summary(
    inst_id: int,
    db: Session = Depends(get_db),
    user=Depends(require_roles(["programme_manager"]))
):
    batches = db.query(Batch).filter(Batch.institution_id == inst_id).all()

    return {"total_batches": len(batches)}


@app.get("/programme/summary")
def programme_summary(
    db: Session = Depends(get_db),
    user=Depends(require_roles(["programme_manager"]))
):
    return {
        "total_users": db.query(User).count(),
        "total_batches": db.query(Batch).count()
    }