from pymongo import MongoClient
from bson import ObjectId
from database import db
from typing import List

# El archivo models.py contiene las definiciones de los modelos que se utilizarán para interactuar con la BBDD. 
# Los modelos definen la estructura de los documentos que se almacenan en las colecciones de MongoDB.

# Definición del modelo de Usuario en MongoDB
class UserModel:
    def __init__(self, id: str, name: str, email: str, password: str):
        self.id = id
        self.name = name
        self.email = email
        self.password = password
        self.events = []  # Lista de IDs de eventos en los que el usuario participa

    # Conversión a documento de MongoDB
    def to_document(self):
        return {
            "id":self.id,
            "name": self.name,
            "email": self.email,
            "password": self.password,
            "events": self.events
        }

    # Conversión de documento de MongoDB a objeto UserModel
    @classmethod
    def from_document(cls, document):
        user = cls(
            id=document["id"],
            name=document["name"],
            email=document["email"],
            password=document["password"]
        )
        user.events = document.get("events", [])
        return user

# Definición del modelo de Evento en MongoDB
class EventModel:
    def __init__(self, id: str, title: str, description: str, creator_id: ObjectId, participants: List[str], date: str):
        self.id = id
        self.title = title
        self.description = description
        self.creator_id = creator_id
        self.participants = []  # Lista de IDs de participantes en el evento
        self.date = date

    # Conversión a documento de MongoDB
    def to_document(self):
        return {
            "_id":self.id,
            "title": self.title,
            "description": self.description,
            "creator_id": self.creator_id,
            "participants": self.participants,
            "date": self.date
        }

    # Conversión de documento de MongoDB a objeto EventModel
    @classmethod
    def from_document(cls, document):
        event = cls(
            _id=document["id"],
            title=document["title"],
            description=document["description"],
            creator_id=document["creator_id"],
            date=document["date"]
        )
        event.participants = document.get("participants", [])
        return event
