from src.database import SessionLocal
from src.models import User, Batch, Session, Attendance, BatchStudent
from src.auth import hash_password
from datetime import datetime

db = SessionLocal()

try:
    # ---------------- INSTITUTION ----------------
    institution = User(
        name="Institution1",
        email="inst1@test.com",
        hashed_password=hash_password("1234"),
        role="institution"
    )
    db.add(institution)
    db.commit()
    db.refresh(institution)

    institution_id = institution.id

    # ---------------- PROGRAMME MANAGER ----------------
    pm = User(
        name="Programme Manager",
        email="pm@test.com",
        hashed_password=hash_password("1234"),
        role="programme_manager"
    )

    # ---------------- MONITORING OFFICER ----------------
    mo = User(
        name="Monitoring Officer",
        email="mo@test.com",
        hashed_password=hash_password("1234"),
        role="monitoring_officer"
    )

    db.add_all([pm, mo])
    db.commit()

    # ---------------- TRAINERS ----------------
    trainers = []
    for i in range(1, 5):
        trainer = User(
            name=f"Trainer{i}",
            email=f"trainer{i}@test.com",
            hashed_password=hash_password("1234"),
            role="trainer",
            institution_id=institution_id
        )
        trainers.append(trainer)

    db.add_all(trainers)
    db.commit()

    # ---------------- STUDENTS ----------------
    students = []
    for i in range(1, 16):
        student = User(
            name=f"Student{i}",
            email=f"student{i}@test.com",
            hashed_password=hash_password("1234"),
            role="student",
            institution_id=institution_id
        )
        students.append(student)

    db.add_all(students)
    db.commit()

    # ---------------- BATCHES ----------------
    batches = []
    for i in range(1, 4):
        batch = Batch(
            name=f"Batch{i}",
            institution_id=institution_id
        )
        batches.append(batch)

    db.add_all(batches)
    db.commit()

    # ---------------- ASSIGN STUDENTS TO BATCH 1 ----------------
    for student in students:
        db.add(BatchStudent(
            batch_id=batches[0].id,
            student_id=student.id
        ))

    db.commit()

    # ---------------- SESSIONS ----------------
    sessions = []
    for i in range(1, 9):
        session = Session(
            batch_id=batches[0].id,
            trainer_id=trainers[0].id,
            title=f"Session{i}",
            date=datetime.utcnow().date(),
            start_time=datetime.utcnow().time(),
            end_time=datetime.utcnow().time()
        )
        sessions.append(session)

    db.add_all(sessions)
    db.commit()

    # ---------------- ATTENDANCE ----------------
    for session in sessions:
        for student in students[:5]:
            db.add(Attendance(
                session_id=session.id,
                student_id=student.id,
                status="present"
            ))

    db.commit()

    print("✅ Seed data inserted successfully!")

except Exception as e:
    db.rollback()
    print("❌ Error during seeding:", e)

finally:
    db.close()