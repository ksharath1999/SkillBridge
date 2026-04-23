from datetime import date, time
from sqlalchemy.orm import Session
from src.database import SessionLocal
from src.models import (
    User,
    Institution,
    Batch,
    BatchStudent,
    Session,
    Attendance
)
from src.auth import hash_password
import random

db: Session = SessionLocal()


def get_or_create(model, filters, defaults={}):
    instance = db.query(model).filter_by(**filters).first()
    if instance:
        return instance

    instance = model(**{**filters, **defaults})
    db.add(instance)
    db.commit()
    db.refresh(instance)
    return instance


def main():
    print("🌱 Seeding database...")

    inst1 = get_or_create(Institution, {"name": "Greenfield Skill Institute"})
    inst2 = get_or_create(Institution, {"name": "Sunrise Technical Academy"})

    trainers = []
    for i in range(4):
        trainers.append(
            get_or_create(User,
                {"email": f"trainer{i}@test.com"},
                {
                    "name": f"Trainer {i}",
                    "hashed_password": hash_password("1234"),
                    "role": "trainer",
                    "institution_id": inst1.id if i < 2 else inst2.id
                }
            )
        )

    students = []
    for i in range(15):
        students.append(
            get_or_create(User,
                {"email": f"student{i}@test.com"},
                {
                    "name": f"Student {i}",
                    "hashed_password": hash_password("1234"),
                    "role": "student",
                    "institution_id": inst1.id if i < 10 else inst2.id
                }
            )
        )

    batch1 = get_or_create(Batch, {"name": "Batch Alpha"}, {"institution_id": inst1.id})
    batch2 = get_or_create(Batch, {"name": "Batch Beta"}, {"institution_id": inst1.id})
    batch3 = get_or_create(Batch, {"name": "Batch Gamma"}, {"institution_id": inst2.id})

    batches = [batch1, batch2, batch3]

    # 🔥 FIX: assign students
    for i, batch in enumerate(batches):
        for student in students[i*5:(i+1)*5]:
            if not db.query(BatchStudent).filter_by(
                batch_id=batch.id,
                student_id=student.id
            ).first():
                db.add(BatchStudent(batch_id=batch.id, student_id=student.id))

    db.commit()

    sessions = []
    for i in range(8):
        session = Session(
            batch_id=batches[i % 3].id,
            trainer_id=trainers[i % 4].id,
            title=f"Session {i}",
            date=date.today(),
            start_time=time(10, 0),
            end_time=time(11, 0)
        )
        db.add(session)
        db.commit()
        db.refresh(session)
        sessions.append(session)

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