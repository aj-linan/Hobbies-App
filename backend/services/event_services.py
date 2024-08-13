from models import EventModel
from schemas import EventCreate, EventUpdate
from database import db  # Conexión a la base de datos
from bson import ObjectId
from typing import List

# Servicio para crear un nuevo evento
async def create_event(event: EventCreate) -> EventModel:
    event_dict = event.dict()
    new_event = await db["events"].insert_one(event_dict)
    event_dict["_id"] = new_event.inserted_id
    return EventModel(**event_dict)

# Servicio para obtener un evento por su ID
async def get_event_by_id(event_id: str) -> EventModel:
    event = await db["events"].find_one({"_id": ObjectId(event_id)})
    if event:
        return EventModel(**event)
    return None

# Servicio para actualizar un evento existente
async def update_event(event_id: str, event: EventUpdate) -> EventModel:
    event_dict = {k: v for k, v in event.dict().items() if v is not None}
    result = await db["events"].update_one(
        {"_id": ObjectId(event_id)}, {"$set": event_dict}
    )
    if result.matched_count == 1:
        return await get_event_by_id(event_id)
    return None

# Servicio para listar todos los eventos
async def list_events() -> List[EventModel]:
    events = await db["events"].find().to_list(length=100)
    return [EventModel(**event) for event in events]
