from pydantic import BaseModel, Field, ConfigDict
from typing import List, Optional
from bson import ObjectId

# El archivo schemas.py contiene las definiciones de los esquemas que se utilizan para 
# validar los datos que entran y salen de tu API

# Definimos un campo personalizado para ObjectId
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
    name: str
    email: str
    events: List[str] = Field(default_factory=list)  # Convertimos ObjectId a str

    # Configuración del modelo
    model_config = ConfigDict(
        from_attributes=True,  # Permite convertir datos desde atributos ORM
        populate_by_name=True,  # Permite popular campos usando nombres de campo alternativos
    )

# Esquema para crear un usuario
class UserCreate(BaseModel):
    id: str = Field(default_factory=str) 
    name: str
    email: str
    password: str

# Esquema para actualizar un usuario
class UserUpdate(BaseModel):
    name: Optional[str]
    email: Optional[str]

# Esquema para leer un evento
class EventRead(BaseModel):
    id: str = Field(default_factory=str)  # Convertimos ObjectId a str
    title: str
    description: str
    creator_id: str  # Convertimos ObjectId a str
    participants: List[str] = Field(default_factory=list)  # Convertimos ObjectId a str
    date: str

# Esquema para crear un evento
class EventCreate(BaseModel):
    title: str
    description: str
    creator_id: str  # Convertimos ObjectId a str
    date: str

# Esquema para actualizar un evento
class EventUpdate(BaseModel):
    title: Optional[str]
    description: Optional[str]
    date: Optional[str]
