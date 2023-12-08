from pydantic import BaseModel
from typing import Literal

class RecommendationReq(BaseModel):
    gender: Literal ["Male", "Female"]
    age: int
    weight: float
    height: float
    activity: Literal ["sedentary", "lightly_active", "moderately_active", "very_active", "extra_active"]
    mood: Literal ["happy", "loved", "focus", "chill", "sad", "scared", "angry", "neutral"] = None
    weather: Literal ["yes", "no"] = None,
    max_rec: int = 5

    class Config:
        json_schema_extra = {
            "example": {
                "gender": "Male",
                "age": 20,
                "weight": 63.0,
                "height": 171.0,
                "activity": ["sedentary", "lightly_active", "moderately_active", "very_active", "extra_active"],
                "mood": ["happy", "loved", "focus", "chill", "sad", "scared", "angry", "neutral"],
                "weather": "['yes', 'no'] - Are you concerned about the weather?",
                "max_rec": 5
            }
        }


class Reservation(BaseModel):
    id_reservation: int
    reserver_name: str
    id_user: int
    id_table: int
    hourstart: int
    duration: int

# Pydantic model for Table
class Table(BaseModel):
    id_table: int
    hourstart: int
    status: bool

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: str

class User(BaseModel):
    username: str
    email: str or None = None
    full_name: str or None = None
    role: str
    password: str

    class Config:
        json_schema_extra = {
            "example": {
                "username" : "username",
                "email" : "email@example.com",
                "full_name" : "full_name",
                "role" : "customer",
                "password" : "string"
            }
        }

class UserInDB(User):
    id_user : int
    username : str
    full_name: str or None = None
    email: str or None = None
    role: str   
    hashed_password: str
    disabled: bool or None = None

class Consultation(BaseModel):
    consultation_date: str
    consultation_time: str

    class Config:
        json_schema_extra = {
            "example": {
                "consultation_date": "2023-12-31",
                "consultation_time": "10:00"
            }
        }