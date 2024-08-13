from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime
from bson import ObjectId

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


# Este es un modelo que describe la estructura de un usuario en la base de datos.
class UserModel(BaseModel):
    id: Optional[ObjectId] = Field(alias="_id")  # El ID es opcional porque MongoDB lo genera automáticamente
    username: str                               # Nombre de usuario
    email: str                                  # Correo electrónico del usuario
    hashed_password: str                        # Contraseña encriptada
    full_name: Optional[str] = None             # Nombre completo del usuario (opcional)
    joined_at: datetime = Field(default_factory=datetime.now(datetime.UTC))  # Fecha en la que se unió el usuario

    class Config:
        allow_population_by_field_name = True
        json_encoders = {ObjectId: str}         # Para manejar la conversión de ObjectId a string
        arbitrary_types_allowed = True          # Permite tipos arbitrarios como ObjectId