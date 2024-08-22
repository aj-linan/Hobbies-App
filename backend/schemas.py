from pydantic import BaseModel, Field
from typing import List, Optional
from bson import ObjectId
from datetime import datetime, UTC

# Campo personalizado para ObjectId
class PyObjectId(ObjectId):
    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v):
        if not ObjectId.is_valid(v):
            raise ValueError('Invalid ObjectId')
        return str(v)

# Esquema para leer un usuario
class UserRead(BaseModel):
    id: str = Field(default_factory=str)  # Convertimos ObjectId a str
    email: str
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    birthdate:Optional[datetime] = None
    interests: List[str] = Field(default_factory=list)
    location: Optional[str] = None
    verified: bool
    groups: Optional[List[str]] = Field(default_factory=list)  # Convertimos ObjectId a str
    created_events: Optional[List[str]] = Field(default_factory=list)  # Convertimos ObjectId a str
    participating_events: Optional[List[str]] = Field(default_factory=list)  # Convertimos ObjectId a str
    created_at: datetime

# Esquema para crear un usuario
class UserCreate(BaseModel):
    email: str
    password: str 
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    birthdate:Optional[datetime] = None
    interests: Optional[List[str]] = Field(default_factory=list)
    location: Optional[str] = None
    profile_visibility: Optional[bool] = True
    verified: Optional[bool] = False
    groups: Optional[List[str]] = Field(default_factory=list)  # Convertimos ObjectId a str
    created_events: Optional[List[str]] = Field(default_factory=list)  # Convertimos ObjectId a str
    participating_events: Optional[List[str]] = Field(default_factory=list)  # Convertimos ObjectId a str

# Esquema para actualizar un usuario
class UserUpdate(BaseModel):
    email: Optional[str]
    first_name: Optional[str]
    last_name: Optional[str]
    interests: Optional[List[str]]
    location: Optional[str]

# Esquema para leer un evento
class EventRead(BaseModel):
    id: str = Field(default_factory=str)  # Convertimos ObjectId a str
    title: str
    description: str
    creator_id: str  # Convertimos ObjectId a str
    participants: List[str] = Field(default_factory=list)  # Convertimos ObjectId a str
    date: str
    max_participants: int
    created_at: datetime
    updated_at: Optional[datetime]

# Esquema para crear un evento
class EventCreate(BaseModel):
    title: str
    description: str
    date: str
    max_participants: Optional[int] = 10

# Esquema para actualizar un evento
class EventUpdate(BaseModel):
    title: Optional[str]
    description: Optional[str]
    date: Optional[str]
    max_participants: Optional[int] = None

# Esquema para leer un grupo
class GroupRead(BaseModel):
    id: str = Field(default_factory=str)  # Convertimos ObjectId a str
    name: str
    description: str
    is_private: bool
    members: List[str] = Field(default_factory=list)  # Convertimos ObjectId a str
    interests: List[str] = Field(default_factory=list)
    created_at: datetime

# Esquema para crear un grupo
class GroupCreate(BaseModel):
    name: str
    description: str
    is_private: bool
    members: Optional[List[str]] = Field(default_factory=list)  # Convertimos ObjectId a str
    interests: Optional[List[str]] = Field(default_factory=list)

# Esquema para actualizar un grupo
class GroupUpdate(BaseModel):
    name: Optional[str]
    description: Optional[str]
    is_private: Optional[bool]
    members: Optional[List[str]] = Field(default_factory=list)
    interests: Optional[List[str]] = Field(default_factory=list)
