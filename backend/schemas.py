# Importamos las librerías necesarias
from pydantic import BaseModel, EmailStr, Field
from typing import List, Optional
from datetime import datetime
from bson import ObjectId

# Esquema para crear un evento
class EventCreate(BaseModel):
    title: str  # Título del evento
    description: Optional[str] = None  # Descripción opcional
    date: datetime  # Fecha y hora
    location: str  # Ubicación
    event_type: str  # Tipo de evento
    requirements: Optional[str] = None  # Requisitos especiales
    creator: str  # ID del creador del evento
    participants: Optional[List[str]] = []  # Lista de IDs de participantes

# Esquema para la respuesta del evento (incluye el ID de MongoDB)
class EventResponse(EventCreate):
    id: str  # ID del evento en MongoDB

    class Config:
        orm_mode = True  # Configuración para compatibilidad con ObjectId de MongoDB

# Este esquema se utiliza para crear un nuevo usuario
class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str

# Este esquema se utiliza para leer datos de un usuario (por ejemplo, al devolver la información de un usuario)
class UserRead(BaseModel):
    id: Optional[ObjectId] = Field(alias="_id")
    username: str
    email: EmailStr
    full_name: Optional[str] = None

    class Config:
        allow_population_by_field_name = True
        json_encoders = {ObjectId: str}

# Este esquema se utiliza para actualizar un usuario existente
class UserUpdate(BaseModel):
    full_name: Optional[str] = None
    email: Optional[EmailStr] = None
    password: Optional[str] = None
