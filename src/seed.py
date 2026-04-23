from datetime import datetime, date, time
from sqlalchemy.orm import Session
from src.database import SessionLocal
from src.models import (
    User,
    Institution,
    Batch,
    BatchTrainer,
    BatchStudent,
    Session,
    Attendance
)
from src.auth import hash_password
import random

db: Session = SessionLocal()


# ---------- HELPERS ----------

def get_or_create(model, filters: dict, defaults: dict = {}):
    instance = db.query(model).filter_by(**filters).first()
    if instance:
        return instance

    params = {**filters, **defaults}
    instance = model(**params)
    db.add(instance)
    db.commit()
    db.refresh(instance)
    return instance


# ---------- MAIN SEED ----------

def main():
    print("🌱 Seeding database...")

    # ---------- Institutions ----------
    inst1 = get_or_create(Institution, {"name": "Greenfield Skill Institute"})
    inst2 = get_or_create(Institution, {"name": "Sunrise Technical Academy"})

    # ---------- Core Users ----------
    get_or_create(User,
        {"email": "admin.greenfield@skillbridge.com"},
        {
            "name": "Admin Greenfield",
            "hashed_password": hash_password("1234"),
            "role": "institution"
        }
    )

    get_or_create(User,
        {"email": "rakesh.menon@skillbridge.com"},
        {
            "name": "Rakesh Menon",
            "hashed_password": hash_password("1234"),
            "role": "programme_manager"
        }
    )

    get_or_create(User,
        {"email": "farah.khan@skillbridge.com"},
        {
            "name": "Farah Khan",
            "hashed_password": hash_password("1234"),
            "role": "monitoring_officer"
        }
    )

    # ---------- Trainers ----------
    trainer_data = [
        ("Amit Sharma", "amit.sharma@skillbridge.com", inst1.id),
        ("Neha Verma", "neha.verma@skillbridge.com", inst1.id),
        ("Rahul Nair", "rahul.nair@skillbridge.com", inst2.id),
        ("Priya Iyer", "priya.iyer@skillbridge.com", inst2.id),
    ]

    trainers = []
    for name, email, inst_id in trainer_data:
        trainers.append(
            get_or_create(User,
                {"email": email},
                {
                    "name": name,
                    "hashed_password": hash_password("1234"),
                    "role": "trainer",
                    "institution_id": inst_id
                }
            )
        )

    # ---------- Students ----------
    student_names = [
        "Arjun Mehta", "Sneha Kapoor", "Rohit Singh", "Ananya Das", "Vikram Patel",
        "Kiran Kumar", "Pooja Reddy", "Aditya Joshi", "Meera Nair", "Sahil Khan",
        "Divya Menon", "Karthik Raj", "Nisha Thomas", "Varun Gupta", "Aisha Ali"
    ]

    students = []
    for i, name in enumerate(student_names):
        email = name.lower().replace(" ", ".") + "@student.com"
        inst_id = inst1.id if i < 10 else inst2.id

        students.append(
            get_or_create(User,
                {"email": email},
                {
                    "name": name,
                    "hashed_password": hash_password("1234"),
                    "role": "student",
                    "institution_id": inst_id
                }
            )
        )

    # ---------- Batches ----------
    batch1 = get_or_create(Batch, {"name": "Batch Alpha"}, {"institution_id": inst1.id})
    batch2 = get_or_create(Batch, {"name": "Batch Beta"}, {"institution_id": inst1.id})
    batch3 = get_or_create(Batch, {"name": "Batch Gamma"}, {"institution_id": inst2.id})

    batches = [batch1, batch2, batch3]

    # ---------- Assign Trainers ----------
    for batch, trainer in zip(batches, trainers):
        if not db.query(BatchTrainer).filter_by(
            batch_id=batch.id, trainer_id=trainer.id
        ).first():
            db.add(BatchTrainer(batch_id=batch.id, trainer_id=trainer.id))

    # ---------- Assign Students ----------
    for i, batch in enumerate(batches):
        batch_students = students[i*5:(i+1)*5]

        for student in batch_students:
            if not db.query(BatchStudent).filter_by(
                batch_id=batch.id, student_id=student.id
            ).first():
                db.add(BatchStudent(batch_id=batch.id, student_id=student.id))

    db.commit()

    # ---------- Sessions ----------
    session_titles = [
        "Python Basics", "Data Structures", "Web Development",
        "Database Fundamentals", "APIs with FastAPI",
        "Authentication Systems", "Testing & Debugging", "Project Review"
    ]

    sessions = []
    for i, title in enumerate(session_titles):
        batch = batches[i % 3]

        existing = db.query(Session).filter_by(title=title).first()
        if existing:
            sessions.append(existing)
            continue

        session = Session(
            batch_id=batch.id,
            trainer_id=trainers[i % 3].id,
            title=title,
            date=date.today(),
            start_time=time(10, 0),
            end_time=time(11, 0)
        )
        db.add(session)
        db.commit()
        db.refresh(session)
        sessions.append(session)

    # ---------- Attendance ----------
    statuses = ["present", "absent", "late"]

    for session in sessions:
        batch_students = db.query(BatchStudent).filter_by(
            batch_id=session.batch_id
        ).all()

        for bs in batch_students:
            if not db.query(Attendance).filter_by(
                session_id=session.id,
                student_id=bs.student_id
            ).first():
                db.add(Attendance(
                    session_id=session.id,
                    student_id=bs.student_id,
                    status=random.choice(statuses)
                ))

    db.commit()

    print("✅ Seeding completed successfully!")


if __name__ == "__main__":
    main()