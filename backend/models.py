from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime

# BaseModel: Es la clase base de Pydantic para definir modelos de datos.
# Optional: Indica que el campo es opcional.
# List[str]: Representa una lista de cadenas de texto (IDs de participantes).

# Definimos el modelo de datos para un evento
class Event(BaseModel):
    title: str  # Título del evento
    description: Optional[str] = None  # Descripción opcional del evento
    date: datetime  # Fecha y hora del evento
    location: str  # Ubicación del evento
    event_type: str  # Tipo de evento (por ejemplo, deportivo, social)
    requirements: Optional[str] = None  # Requisitos especiales (opcional)
    creator: str  # ID del usuario que creó el evento
    participants: Optional[List[str]] = []  # Lista de IDs de participantes