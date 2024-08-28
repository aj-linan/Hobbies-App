from pydantic import BaseModel, Field, EmailStr
from typing import List, Optional
from bson import ObjectId
from datetime import datetime

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
    email: EmailStr
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    birthdate:Optional[datetime] = None
    interests: List[str] = Field(default_factory=list)
    location: Optional[str] = None
    verified: bool = False
    groups: Optional[List[str]] = Field(default_factory=list)  # Convertimos ObjectId a str
    created_groups: Optional[List[str]] = Field(default_factory=list) 
    created_events: Optional[List[str]] = Field(default_factory=list)  # Convertimos ObjectId a str
    participating_events: Optional[List[str]] = Field(default_factory=list)  # Convertimos ObjectId a str
    created_at: datetime

# Esquema para crear un usuario
class UserCreate(BaseModel):
    email: EmailStr
    password: str 
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    birthdate:Optional[datetime] = None
    interests: Optional[List[str]] = Field(default_factory=list)
    location: Optional[str] = None
    verified: bool = False


# Esquema para actualizar un usuario
class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    interests: Optional[List[str]] = None
    location: Optional[str] = None

# Esquema para leer un evento
class EventRead(BaseModel):
    id: str = Field(default_factory=str)  # Convertimos ObjectId a str
    title: str
    description: str
    creator_id: str  # Convertimos ObjectId a str
    participants: Optional[List[str]] = Field(default_factory=list)  # Convertimos ObjectId a str
    date: str
    max_participants: int
    created_at: datetime
    updated_at: datetime

# Esquema para crear un evento
class EventCreate(BaseModel):
    title: str
    description: str
    date: str
    max_participants: Optional[int] = 10

# Esquema para actualizar un evento
class EventUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    date: Optional[str] = None
    max_participants: Optional[int] = None
    participants: Optional[List[str]] = Field(default_factory=list)
    updated_at: Optional[datetime] = None

    @classmethod
    def from_db(cls, db_data: dict) -> 'EventUpdate':
        # Convertir ObjectId a str
        db_data['participants'] = [str(pid) for pid in db_data.get('participants', [])]
        return cls(**db_data)
    
    def to_db(self) -> dict:
        # Convertir str a ObjectId
        db_data = self.model_dump()
        db_data['participants'] = [ObjectId(pid) for pid in db_data['participants']]
        return db_data

# Esquema para leer un grupo
class GroupRead(BaseModel):
    id: str = Field(default_factory=str)  # Convertimos ObjectId a str
    name: str
    description: str
    is_private: bool = False
    creator_id: str
    members: List[str] = Field(default_factory=list)  # Convertimos ObjectId a str
    interests: List[str] = Field(default_factory=list)
    created_at: datetime
    max_participants: int

# Esquema para crear un grupo
class GroupCreate(BaseModel):
    name: str
    description: str
    is_private: bool = False
    interests: Optional[List[str]] = Field(default_factory=list)
    max_participants: Optional[int] = 10

# Esquema para actualizar un grupo
class GroupUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    members: Optional[List[str]] = Field(default_factory=list)
    interests: Optional[List[str]] = Field(default_factory=list)
    updated_at: datetime = None

    @classmethod
    def from_db(cls, db_data: dict) -> 'EventUpdate':
        # Convertir ObjectId a str
        db_data['members'] = [str(pid) for pid in db_data.get('members', [])]
        return cls(**db_data)
    
    def to_db(self) -> dict:
        # Convertir str a ObjectId
        db_data = self.model_dump()
        db_data['members'] = [ObjectId(pid) for pid in db_data['members']]
        return db_data
