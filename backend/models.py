from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime, timezone
from bson import ObjectId

# Modelo de Usuario
class UserModel(BaseModel):
    id: str
    email: str
    password: str
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    interests: List[str] = Field(default_factory=list)
    location: Optional[str] = None
    profile_visibility: bool = True
    groups: List[str] = Field(default_factory=list)  # Lista de IDs de los grupos a los que pertenece el usuario
    created_events: List[str] = Field(default_factory=list)  # Lista de IDs de eventos creados por el usuario
    participating_events: List[str] = Field(default_factory=list)  # Lista de IDs de eventos en los que participa el usuario
    created_at: datetime = Field(default_factory=lambda: datetime.now(tz=timezone.utc))  # Fecha de creación del usuario
    
    class Config:
        json_encoders = {
            ObjectId: str
        }

# Modelo de Evento
class EventModel(BaseModel):
    id: str 
    title: str
    description: str
    creator_id: str  # ID del creador del evento
    participants: List[str] = Field(default_factory=list)  # Lista de IDs de participantes en el evento
    date: str
    max_participants: int = 10  # Número máximo de participantes
    created_at: datetime = Field(default_factory=lambda: datetime.now(tz=timezone.utc))  # Fecha de creación del evento
    updated_at: Optional[datetime] = None  # Fecha de última actualización del evento

    class Config:
        json_encoders = {
            ObjectId: str
        }

# Modelo de Grupo
class GroupModel(BaseModel):
    id: str
    name: str
    description: str
    is_private: bool  # Indica si el grupo es privado o público
    members: List[str] = Field(default_factory=list)  # Lista de IDs de miembros del grupo
    interests: List[str] = Field(default_factory=list)  # Lista de intereses del grupo
    created_at: datetime = Field(default_factory=lambda: datetime.now(tz=timezone.utc))  # Fecha de creación del grupo
    
    class Config:
        json_encoders = {
            ObjectId: str
        }