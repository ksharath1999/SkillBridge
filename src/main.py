from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime
import uuid

from src.database import engine, get_db
from src.models import Base, User, Batch, Session as DBSession, Attendance, BatchInvite, BatchStudent
from src.schemas import UserCreate, UserLogin
from src.auth import hash_password, verify_password, create_access_token, require_roles

app = FastAPI()

Base.metadata.create_all(bind=engine)


@app.get("/")
def root():
    return {"message": "API running"}


# ---------------- AUTH ----------------
@app.post("/auth/signup")
def signup(user: UserCreate, db: Session = Depends(get_db)):
    if db.query(User).filter(User.email == user.email).first():
        raise HTTPException(status_code=400, detail="Email exists")

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
def create_batch(name: str, db: Session = Depends(get_db),
                 user=Depends(require_roles(["trainer", "institution"]))):

    batch = Batch(name=name, institution_id=user.get("institution_id"))
    db.add(batch)
    db.commit()
    return {"id": batch.id}


# ---------------- SESSION ----------------
@app.post("/sessions")
def create_session(batch_id: int, title: str,
                   db: Session = Depends(get_db),
                   user=Depends(require_roles(["trainer"]))):

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

    return {"id": session.id}


# ---------------- INVITE ----------------
@app.post("/batches/{batch_id}/invite")
def invite(batch_id: int, db: Session = Depends(get_db),
           user=Depends(require_roles(["trainer"]))):

    token = str(uuid.uuid4())

    invite = BatchInvite(
        batch_id=batch_id,
        token=token,
        created_by=user["user_id"],
        expires_at=datetime.utcnow()
    )

    db.add(invite)
    db.commit()

    return {"token": token}


# ---------------- JOIN ----------------
@app.post("/batches/join")
def join(token: str, db: Session = Depends(get_db),
         user=Depends(require_roles(["student"]))):

    invite = db.query(BatchInvite).filter(BatchInvite.token == token).first()

    if not invite or invite.used:
        raise HTTPException(status_code=400, detail="Invalid invite")

    db.add(BatchStudent(
        batch_id=invite.batch_id,
        student_id=user["user_id"]
    ))

    invite.used = True
    db.commit()

    return {"message": "Joined"}


# ---------------- ATTENDANCE ----------------
@app.post("/attendance/mark")
def mark(session_id: int, status: str,
         db: Session = Depends(get_db),
         user=Depends(require_roles(["student"]))):

    session = db.query(DBSession).filter(DBSession.id == session_id).first()

    enrolled = db.query(BatchStudent).filter(
        BatchStudent.batch_id == session.batch_id,
        BatchStudent.student_id == user["user_id"]
    ).first()

    if not enrolled:
        raise HTTPException(status_code=403)

    db.add(Attendance(
        session_id=session_id,
        student_id=user["user_id"],
        status=status
    ))

    db.commit()

    return {"message": "marked"}