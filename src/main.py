from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session

from src.database import engine, get_db
from src.models import Base, User
from src.schemas import UserCreate, UserLogin
from src.auth import hash_password, verify_password, create_access_token

app = FastAPI()

Base.metadata.create_all(bind=engine)


@app.post("/auth/signup")
def signup(user: UserCreate, db: Session = Depends(get_db)):
    # check if user exists
    existing_user = db.query(User).filter(User.email == user.email).first()
    if existing_user:
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
        "role": new_user.role
    })

    return {"access_token": token}


@app.post("/auth/login")
def login(user: UserLogin, db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.email == user.email).first()

    if not db_user or not verify_password(user.password, db_user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    token = create_access_token({
        "user_id": db_user.id,
        "role": db_user.role
    })

    return {"access_token": token}