from models import EventModel
from schemas import EventCreate, EventUpdate
from database import db  # Conexión a la base de datos
from bson import ObjectId
from typing import List

# El archivo event_services.py contiene la lógica de negocio de la aplicación. 
# Este archivo actúa como una capa de servicio que encapsula la lógica para interactuar con los modelos y esquemas.

# Servicio para crear un nuevo evento
async def create_event(user_id: str, event: EventCreate) -> EventModel:
    event_dict = event.model_dump()
    event_dict["creator_id"] = user_id
    # Importante tener en cuenta que cuando se sube a la base de datos. 
    # Event_dict se modifica tambien
    new_event = await db.get_collection("events").insert_one(event_dict)
    event_dict["id"] = str(new_event.inserted_id)
    event_dict.pop("_id")
    
    return EventModel(**event_dict)

# Servicio para obtener un evento por su ID
async def get_event_by_id(event_id: str) -> EventModel:
    event = await db.get_collection("events").find_one({"_id": ObjectId(event_id)})
    event["id"] = str(event["_id"] )
    event.pop("_id")
    if event:
        return EventModel(**event)
    return None

# Servicio para obtener todos los eventos de un usuario por su ID
async def get_events_by_user_id(user_id: str) -> List[EventModel]:
    
    pipeline = [
        {
            "$match": {
                "creator_id": user_id  # Filter by user ID
            }
        },
        {
            "$project": {
                "id": {"$toString": "$_id"},  # Convert _id to string and rename to id
                "_id": 0,  # Exclude the original _id field
                "title": 1,  # Include the title field
                "description": 1,  # Include the description field
                "creator_id": 1,  # Include the creator_id field
                "date": 1  # Include the date field
            }
        }
    ]

    # Run the aggregation pipeline
    events = await db.get_collection("events").aggregate(pipeline).to_list(length=100)
    print(events)

    return [EventModel(**event) for event in events]
    
# Servicio para actualizar un evento existente
async def update_event(event_id: str, event: EventUpdate) -> EventModel:

    event_dict = {k: v for k, v in event.model_dump().items() if v is not None}
    result = await db.get_collection("events").update_one(
        {"_id": ObjectId(event_id)}, {"$set": event_dict}
    )
    if result.matched_count == 1:
        return await get_event_by_id(event_id)
    return None

# Servicio para listar todos los eventos
async def list_events() -> List[EventModel]:
    
    pipeline = [
        {
            "$project": {
                "id": {"$toString": "$_id"},
                "_id": 0,
                "title":1, 
                "description":1, 
                "creator_id":1,
                "date":1

            }
        }
    ]

    events = await db.get_collection("events").aggregate(pipeline).to_list(length=100)

    return [EventModel(**event) for event in events]


