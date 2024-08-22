from models import EventModel
from schemas import EventCreate, EventUpdate
from database import db  # Conexión a la base de datos
from bson import ObjectId
from typing import List
from fastapi import HTTPException

# El archivo event_services.py contiene la lógica de negocio de la aplicación. 
# Este archivo actúa como una capa de servicio que encapsula la lógica para interactuar con los modelos y esquemas.

# Servicio para crear un nuevo evento
async def create_event(user_id: str, event: EventCreate) -> EventModel:
    event_dict = event.model_dump()
    event_dict["creator_id"] = ObjectId(user_id)
    
    # Crear el evento en la base de datos
    new_event = await db.get_collection("events").insert_one(event_dict)
    event_dict["id"] = str(new_event.inserted_id)
    event_dict["creator_id"] = str(user_id)
    event_dict.pop("_id")
    
    # Actualizar el usuario para añadir el ID del evento a la lista de eventos creados
    result = await db.get_collection("users").update_one(
        {"_id": ObjectId(user_id)},
        {"$push": {"created_events": new_event.inserted_id}}
    )
    
    # Verificar si la actualización del usuario fue exitosa
    if result.modified_count != 1:
        raise HTTPException(status_code=500, detail="Error al actualizar el usuario con el nuevo evento.")
    
    return EventModel(**event_dict)


# Servicio para obtener un evento por su ID
async def get_event_by_id(event_id: str) -> EventModel:

    # Recupera datos de la base de datos
    db_data = await db.get_collection("events").find_one({"_id": ObjectId(event_id)})
    if db_data:
        # Convierte datos de la base de datos a un modelo de Pydantic
        return EventModel.from_db(db_data)
    raise HTTPException(status_code=404, detail="Event not found")

# Servicio para obtener todos los eventos de un usuario por su ID
async def get_events_by_user_id(user_id: str) -> List[EventModel]:
    
    try:
        
        # Buscar los eventos que coincidan con el creator_id
        cursor = db.get_collection("events").find({"creator_id": ObjectId(user_id)})
        
        # Convertir los documentos de la base de datos a instancias de EventModel
        events = []
        async for db_event in cursor:
            events.append(EventModel.from_db(db_event))
        
        return events
    
    except Exception as e:
        # Manejar el error apropiadamente
        print(f"An error occurred: {e}")
        raise HTTPException(status_code=500, detail="An error occurred while retrieving events.")
    
    
# Servicio para actualizar un evento existente
async def update_event(event_id: str, event: EventUpdate) -> EventModel:

    # Convertir el modelo a diccionario y filtrar campos nulos
    event_dict = event.model_dump()

    # Filtrar valores nulos, vacíos y listas vacías
    filtered_event_dict = {k: v for k, v in event_dict.items() if v not in [None, "", [], {}]}

    # Verificar si hay campos para actualizar
    if not filtered_event_dict:
        raise HTTPException(status_code=400, detail="No fields to update")

    # Actualizar el usuario en la base de datos
    result = await db.get_collection("events").update_one(
        {"_id": ObjectId(event_id)}, {"$set": filtered_event_dict}
    )

    # Verificar si la actualización fue exitosa
    if result.matched_count == 1:
        # Obtener y retornar el usuario actualizado
        return await get_event_by_id(event_id)
    
    return None

# Servicio para listar todos los eventos
async def list_events() -> List[EventModel]:

    try:
        cursor = db.get_collection("events").find()
        events = []
        async for db_event in cursor:
            events.append(EventModel.from_db(db_event))
        return events
    except Exception as e:
        raise HTTPException(status_code=500, detail="Error retrieving events")


