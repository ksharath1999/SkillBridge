from src.database import SessionLocal
from src.models import User, Batch, Session, Attendance, BatchStudent
from src.auth import hash_password
from datetime import datetime

db = SessionLocal()

# ---- USERS ----
users = [
    User(name="Inst1", email="inst1@test.com", hashed_password=hash_password("1234"), role="institution"),
    User(name="PM", email="pm@test.com", hashed_password=hash_password("1234"), role="programme_manager"),
    User(name="MO", email="mo@test.com", hashed_password=hash_password("1234"), role="monitoring_officer"),
]

trainers = [
    User(name=f"Trainer{i}", email=f"trainer{i}@test.com",
         hashed_password=hash_password("1234"), role="trainer")
    for i in range(1, 5)
]

students = [
    User(name=f"Student{i}", email=f"student{i}@test.com",
         hashed_password=hash_password("1234"), role="student")
    for i in range(1, 16)
]

all_users = users + trainers + students
db.add_all(all_users)
db.commit()

# ---- BATCHES ----
batches = [
    Batch(name=f"Batch{i}", institution_id=1)
    for i in range(1, 4)
]

db.add_all(batches)
db.commit()

# ---- ASSIGN STUDENTS ----
for student in students:
    db.add(BatchStudent(batch_id=1, student_id=student.id))

db.commit()

# ---- SESSIONS ----
sessions = [
    Session(
        batch_id=1,
        trainer_id=4,
        title=f"Session{i}",
        date=datetime.utcnow().date(),
        start_time=datetime.utcnow().time(),
        end_time=datetime.utcnow().time()
    )
    for i in range(1, 9)
]

db.add_all(sessions)
db.commit()

# ---- ATTENDANCE ----
for session in sessions:
    for student in students[:5]:
        db.add(Attendance(
            session_id=session.id,
            student_id=student.id,
            status="present"
        ))

db.commit()

print("✅ Seed data inserted!")