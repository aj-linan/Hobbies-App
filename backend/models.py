from pydantic import BaseModel, Field, EmailStr
from typing import List, Optional
from datetime import datetime, timezone
from bson import ObjectId

# Modelo de Usuario
class UserModel(BaseModel):

    id: str
    email: EmailStr
    password: str
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    birthdate:Optional[datetime] = Field(default_factory=datetime)
    interests: Optional[List[str]] = Field(default_factory=list)
    location: Optional[str] = None
    profile_visibility: bool = True
    verified: bool = False
    groups: Optional[List[str]] = Field(default_factory=list)  # Lista de IDs de los grupos a los que pertenece el usuario
    created_events: Optional[List[str]] = Field(default_factory=list)  # Lista de IDs de eventos creados por el usuario
    created_groups: Optional[List[str]] = Field(default_factory=list)  # Lista de IDs de eventos creados por el usuario
    participating_events: Optional[List[str]] = Field(default_factory=list)  # Lista de IDs de eventos en los que participa el usuario
    created_at: datetime  # Fecha de creación del usuario

    @classmethod
    def from_db(cls, data):
        # Convierte los campos ObjectId a str y maneja el formato datetime
        data['id'] = str(data['_id'])
        data['groups'] = [str(g) for g in data.get('groups', [])]
        data['created_events'] = [str(e) for e in data.get('created_events', [])]
        data['created_groups'] = [str(e) for e in data.get('created_groups', [])]
        data['participating_events'] = [str(e) for e in data.get('participating_events', [])]

        return cls(**data)

    def to_db(self):
        # Convierte los campos a ObjectId y maneja el formato datetime
        db_data = {
            "_id": ObjectId(self.id),
            "groups": [ObjectId(g) for g in self.groups],
            "created_events": [ObjectId(e) for e in self.created_events],
            "created_groups": [ObjectId(e) for e in self.created_groups],
            "participating_events": [ObjectId(e) for e in self.participating_events]
        }
        return db_data
    
# Modelo de Evento
class EventModel(BaseModel):

    id: str 
    title: str
    description: str
    creator_id: str  # ID del creador del evento
    participants: Optional[List[str]] = Field(default_factory=list)  # Lista de IDs de participantes en el evento
    date: str
    max_participants: int = 10  # Número máximo de participantes
    created_at: Optional[datetime] # Fecha de creación del evento
    updated_at: Optional[datetime] = None  # Fecha de última actualización del evento

    @classmethod
    def from_db(cls, db_data: dict) -> 'EventModel':
        # Convertir ObjectId a str
        db_data['id'] = str(db_data['_id'])
        db_data['creator_id'] = str(db_data.get('creator_id', ''))
        db_data['participants'] = [str(pid) for pid in db_data.get('participants', [])]
        return cls(**db_data)
    
    def to_db(self) -> dict:
        # Convertir str a ObjectId
        db_data = self.model_dump()
        db_data['_id'] = ObjectId(db_data['id'])
        db_data['creator_id'] = ObjectId(db_data['creator_id'])
        db_data['participants'] = [ObjectId(pid) for pid in db_data['participants']]
        return db_data

# Modelo de Grupo
class GroupModel(BaseModel):

    id: str
    name: str
    description: str
    is_private: bool = False # Indica si el grupo es privado o público
    creator_id: str
    members: Optional[List[str]] = Field(default_factory=list)  # Lista de IDs de miembros del grupo
    interests: Optional[List[str]] = Field(default_factory=list)  # Lista de intereses del grupo
    created_at: Optional[datetime] # Fecha de creación del grupo
    updated_at: Optional[datetime] = None  # Fecha de última actualización del evento
    max_participants: Optional[int] = 10

    @classmethod
    def from_db(cls, db_data: dict) -> 'EventModel':
        # Convertir ObjectId a str
        db_data['id'] = str(db_data['_id'])
        db_data['creator_id'] = str(db_data.get('creator_id', ''))
        db_data['members'] = [str(pid) for pid in db_data.get('members', [])]
        return cls(**db_data)
    
    def to_db(self) -> dict:
        # Convertir str a ObjectId
        db_data = self.model_dump()
        db_data['_id'] = ObjectId(db_data['id'])
        db_data['creator_id'] = ObjectId(db_data['creator_id'])
        db_data['members'] = [ObjectId(pid) for pid in db_data['members']]
        return db_data