# 🚀 SkillBridge API

A role-based training management backend built with FastAPI, PostgreSQL (Neon), and JWT authentication.

---

# 🌐 Live API

Base URL:  
https://skillbridge-xtry.onrender.com/docs

### Deployment Notes
- Backend deployed on Render
- Database hosted on Neon (PostgreSQL)
- Environment variables configured via platform dashboard
- Tables are created automatically using SQLAlchemy `create_all()`

---

# 🔐 Test Accounts (Seeded)

| Role | Email | Password |
|------|------|---------|
| Institution | admin.greenfield@skillbridge.com | 1234 |
| Trainer | trainer0@test.com | 1234 |
| Student | student0@test.com | 1234 |
| Programme Manager | rakesh.menon@skillbridge.com | 1234 |
| Monitoring Officer | farah.khan@skillbridge.com | 1234 |

---

# 🔑 Login (Live Example)

```bash
curl -X POST https://skillbridge-xtry.onrender.com/auth/login \
-H "Content-Type: application/json" \
-d '{
  "email": "trainer0@test.com",
  "password": "1234"
}'

Response:

{
  "access_token": "..."
}
🔐 Using JWT

Authorization: Bearer <access_token>

⚙️ Local Setup (From Scratch)
git clone <your-repo-url>
cd skillbridge-api

python -m venv venv
venv\Scripts\activate

pip install -r requirements.txt

Create .env file:

DATABASE_URL=your_neon_db_url
SECRET_KEY=your_secret_key
MONITORING_API_KEY=12345

Run app:

uvicorn src.main:app --reload

Seed database:

python -m src.seed
📌 API Endpoints + CURL
🔐 Signup
curl -X POST https://skillbridge-xtry.onrender.com/auth/signup \
-H "Content-Type: application/json" \
-d '{
  "name": "Test User",
  "email": "test@test.com",
  "password": "1234",
  "role": "student",
  "institution_id": 1
}'
🔐 Login
curl -X POST https://skillbridge-xtry.onrender.com/auth/login \
-H "Content-Type: application/json" \
-d '{"email":"student0@test.com","password":"1234"}'
📦 Create Batch
curl -X POST "http://localhost:8000/batches?name=BatchX" \
-H "Authorization: Bearer <token>"
🎟 Create Invite
curl -X POST https://skillbridge-xtry.onrender.com/batches/1/invite \
-H "Authorization: Bearer <trainer_token>"
👨‍🎓 Join Batch
curl -X POST "https://skillbridge-xtry.onrender.com/batches/join?token=INVITE_TOKEN" \
-H "Authorization: Bearer <student_token>"

📅 Create Session
curl -X POST "http://localhost:8000/sessions?batch_id=1&title=Session1" \
-H "Authorization: Bearer <trainer_token>"

🧾 Mark Attendance
curl -X POST "http://localhost:8000/attendance/mark?session_id=1&status=present" \
-H "Authorization: Bearer <student_token>"
👁 Monitoring (GET only)
curl http://localhost:8000/monitoring/attendance \
-H "x-api-key: 12345"

❌ Monitoring POST (Expected 405)
curl -X POST http://localhost:8000/monitoring/attendance

📊 Batch Summary
curl http://localhost:8000/batches/1/summary \
-H "Authorization: Bearer <institution_token>"

📊 Programme Summary
curl http://localhost:8000/programme/summary \
-H "Authorization: Bearer <programme_manager_token>"

🧠 Schema Decisions
batch_students

Handles student enrollment into batches.

batch_invites
Token-based joining system
Single-use
Expiry supported
Attendance
Unique constraint on (session_id, student_id)
Prevents duplicate entries
Monitoring Officer (Dual Token Approach)
Uses API key instead of JWT
Read-only access
Separate authentication flow

⚠️ Validation & Error Handling
422 → invalid input
404 → missing resource
403 → unauthorized access
401 → missing/invalid token
405 → invalid method

🧪 Tests
python -m pytest

✔ 5 required tests implemented
✔ Uses real database

✅ What’s Working
Authentication (JWT)
Role-based access
Batch + invite system
Session creation
Attendance tracking
Monitoring endpoint
Summary endpoints
Seed script
Deployment
Tests

⚠️ Partial / Simplifications

No Alembic migrations
Minimal validation schemas
No pagination/filtering

💡 What I Would Do Differently

Add Alembic migrations
Improve validation schemas
Add batch-trainer mapping
Increase test coverage
Add analytics endpoints

🧩 Honest Note

The most challenging part was debugging database schema synchronization.
At multiple points, models were updated but tables were not recreated, causing runtime errors.
This was resolved by enforcing proper table creation before seeding and ensuring consistent DB usage across environments.

📞 CONTACT

Name: Your Name
Email: your@email.com

Phone: your phone number
GitHub: your GitHub profile

Most challenging part:
Debugging database schema sync issues and ensuring consistent behavior across local and deployed environments.