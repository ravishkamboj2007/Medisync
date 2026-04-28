from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

from schemas import (
    ChatRequest, ChatResponse,
    UserRegister, UserLogin, UserResponse,
    AppointmentCreate, AppointmentResponse,
    HealthRecordCreate, HealthRecordResponse
)
from rag import retrieve_context
from ai import role_based_ai
from database import engine, SessionLocal
from dependencies import get_db
import models
from auth import hash_password, verify_password, create_token

# Create all tables on startup
models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="MediSync API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def home():
    return {"message": "Medisync Backend Running"}


# ── AUTH ──────────────────────────────────────────────────────────────────────

@app.post("/auth/register", response_model=UserResponse)
def register(user: UserRegister, db: Session = Depends(get_db)):
    existing = db.query(models.User).filter(models.User.email == user.email).first()
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")
    hashed = hash_password(user.password)
    new_user = models.User(name=user.name, email=user.email, password=hashed, role=user.role)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user


@app.post("/auth/login")
def login(user: UserLogin, db: Session = Depends(get_db)):
    db_user = db.query(models.User).filter(models.User.email == user.email).first()
    if not db_user or not verify_password(user.password, db_user.password):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    token = create_token({"sub": str(db_user.id), "role": db_user.role})
    return {
        "token": token,
        "user": {"id": db_user.id, "name": db_user.name, "email": db_user.email, "role": db_user.role}
    }


# ── USERS ─────────────────────────────────────────────────────────────────────

@app.get("/users/doctors")
def get_doctors(db: Session = Depends(get_db)):
    doctors = db.query(models.User).filter(models.User.role == "doctor").all()
    return [{"id": d.id, "name": d.name, "email": d.email} for d in doctors]


# ── APPOINTMENTS ──────────────────────────────────────────────────────────────

@app.post("/appointments", response_model=AppointmentResponse)
def create_appointment(appt: AppointmentCreate, db: Session = Depends(get_db)):
    new_appt = models.Appointment(**appt.dict())
    db.add(new_appt)
    db.commit()
    db.refresh(new_appt)
    return new_appt


@app.get("/appointments/doctor/{doctor_id}")
def get_doctor_appointments(doctor_id: int, db: Session = Depends(get_db)):
    appts = db.query(models.Appointment).filter(models.Appointment.doctor_id == doctor_id).all()
    result = []
    for a in appts:
        patient = db.query(models.User).filter(models.User.id == a.patient_id).first()
        result.append({
            "id": a.id,
            "patient_name": patient.name if patient else "Unknown",
            "date": str(a.date),
            "time": a.time,
            "status": a.status
        })
    return result


@app.get("/appointments/patient/{patient_id}")
def get_patient_appointments(patient_id: int, db: Session = Depends(get_db)):
    appts = db.query(models.Appointment).filter(models.Appointment.patient_id == patient_id).all()
    result = []
    for a in appts:
        doctor = db.query(models.User).filter(models.User.id == a.doctor_id).first()
        result.append({
            "id": a.id,
            "doctor_name": doctor.name if doctor else "Unknown",
            "date": str(a.date),
            "time": a.time,
            "status": a.status
        })
    return result


# ── HEALTH RECORDS ────────────────────────────────────────────────────────────

@app.post("/health-records", response_model=HealthRecordResponse)
def create_health_record(record: HealthRecordCreate, db: Session = Depends(get_db)):
    new_record = models.HealthRecord(**record.dict())
    db.add(new_record)
    db.commit()
    db.refresh(new_record)
    return new_record


@app.get("/health-records/{patient_id}")
def get_health_records(patient_id: int, db: Session = Depends(get_db)):
    records = db.query(models.HealthRecord).filter(models.HealthRecord.patient_id == patient_id).all()
    return [{"id": r.id, "patient_id": r.patient_id, "bp": r.bp, "sugar": r.sugar, "report_text": r.report_text} for r in records]


# ── AI CHAT ───────────────────────────────────────────────────────────────────

@app.post("/chat", response_model=ChatResponse)
def chat(request: ChatRequest):
    try:
        context = retrieve_context(request.message)
        response = role_based_ai(request.role, request.message, context)
        return {"response": response}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing chat: {str(e)}")
