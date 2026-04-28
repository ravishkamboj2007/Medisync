from pydantic import BaseModel, EmailStr
from datetime import date
from typing import Optional

# USER SCHEMAS

class UserRegister(BaseModel):
    name: str
    email: EmailStr
    password: str
    role: str  # doctor or patient


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class UserResponse(BaseModel):
    id: int
    name: str
    email: EmailStr
    role: str

    class Config:
        from_attributes = True

# APPOINTMENT SCHEMAS

class AppointmentCreate(BaseModel):
    doctor_id: int
    patient_id: int
    date: date
    time: str


class AppointmentResponse(BaseModel):
    id: int
    doctor_id: int
    patient_id: int
    date: date
    time: str
    status: str

    class Config:
        from_attributes = True

# HEALTH RECORD SCHEMAS

class HealthRecordCreate(BaseModel):
    patient_id: int
    bp: str
    sugar: str
    report_text: str


class HealthRecordResponse(BaseModel):
    id: int
    patient_id: int
    bp: str
    sugar: str
    report_text: str

    class Config:
        from_attributes = True


# AI CHAT SCHEMAS

class ChatRequest(BaseModel):
    role: str
    message: str


class ChatResponse(BaseModel):
    response: str