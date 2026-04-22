from fastapi import FastAPI
from src.database import engine
from src.models import Base

app = FastAPI()

# CREATE TABLES
Base.metadata.create_all(bind=engine)


@app.get("/")
def root():
    return {"message": "SkillBridge API running 🚀"}