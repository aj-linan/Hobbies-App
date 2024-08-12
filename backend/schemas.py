# Importamos las librerías necesarias
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

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
