from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field, EmailStr, ConfigDict

class RegisterRequest(BaseModel):
    name: str = Field(min_length=2, max_length=80)
    email: str = Field(min_length=5, max_length=160)
    password: str = Field(min_length=6, max_length=128)

class LoginRequest(BaseModel):
    email: str
    password: str

class HomeRequest(BaseModel):
    budget: float = Field(gt=0)
    room_type: str = Field(min_length=2, max_length=50)
    style: str = Field(default="Modern", max_length=50)
    items: Dict[str, int] = Field(default_factory=dict)
    notes: str = Field(default="", max_length=1000)

class PartyRequest(BaseModel):
    budget: float = Field(gt=0)
    guests: int = Field(gt=0, le=10000)
    event_type: str = Field(min_length=2, max_length=60)
    venue: str = Field(default="Any", max_length=100)
    food_preference: str = Field(default="Mixed", max_length=100)
    notes: str = Field(default="", max_length=1000)

class JewelryRequest(BaseModel):
    budget: float = Field(gt=0)
    occasion: str = Field(min_length=2, max_length=80)
    style: str = Field(default="Elegant", max_length=80)
    outfit_color: str = Field(default="", max_length=80)
    notes: str = Field(default="", max_length=1000)

class RecommendationResponse(BaseModel):
    planner_type: str
    summary: str
    budget: float
    allocation: Dict[str, float]
    recommendations: List[Dict[str, Any]]
    source: str
    image_analysis: Optional[str] = None
