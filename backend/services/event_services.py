from models import EventModel
from schemas import EventCreate, EventUpdate
from database import db  # Conexión a la base de datos
from bson import ObjectId
from typing import List
from fastapi import HTTPException
from datetime import datetime, timezone

# El archivo event_services.py contiene la lógica de negocio de la aplicación. 
# Este archivo actúa como una capa de servicio que encapsula la lógica para interactuar con los modelos y esquemas.

# Servicio para crear un nuevo evento
async def create_event(user_id: str, event: EventCreate) -> EventModel:
    event_dict = event.model_dump()
    event_dict["creator_id"] = ObjectId(user_id)
    event_dict["created_at"] = datetime.now(tz=timezone.utc)

    # Crear el evento en la base de datos
    new_event = await db.get_collection("events").insert_one(event_dict)
    event_dict["id"] = str(new_event.inserted_id)
    event_dict["creator_id"] = str(user_id)
    event_dict.pop("_id")    
    
    # Actualizar el usuario para añadir el ID del evento a la lista de eventos creados
    result = await db.get_collection("users").update_one(
        {"_id": ObjectId(user_id)},
        {"$addToSet": {"created_events": new_event.inserted_id}}
    )
    
    # Verificar si la actualización del usuario fue exitosa
    if result.modified_count != 1:
        raise HTTPException(status_code=500, detail="Error updating the user")
    
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
        raise HTTPException(status_code=500, detail="An error occurred while retrieving events.")
    
    
# Servicio para actualizar un evento existente
async def update_event(event_id: str, event: EventUpdate) -> EventModel:

    # Primero se transforma el modelo a modelo de database
    event_dict = EventUpdate.to_db(event)

    # Filtrar valores nulos, vacíos y listas vacías
    filtered_event_dict = {k: v for k, v in event_dict.items() if v not in [None, "", [], {}]}

    # Verificar si hay campos para actualizar
    if not filtered_event_dict:
        raise HTTPException(status_code=400, detail="No fields to update")

    filtered_event_dict["updated_at"] = datetime.now(tz=timezone.utc)
    
    # Actualizar el evento en la base de datos
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


async def add_user_to_event(eventId: str, userId: str) -> object:

    # Buscar el evento
    event = await get_event_by_id(eventId)
    
    # Verificar que el evento existe
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")
    
     # Verificar si se ha alcanzado el límite máximo de participantes
    if len(event.participants) >= event.max_participants:
        raise HTTPException(status_code=400, detail="Event is already full")

    # Verificar si el usuario ya es un participante
    if userId in event.participants:
        raise HTTPException(status_code=400, detail="User already added to this event")
    
    try:
        # Convertir el user_id a ObjectId
        object_id = ObjectId(userId)

        # Buscar el usuario en la colección "users"
        await db.get_collection("users").find_one({"_id": object_id})
    
    except Exception as e:
        # Manejar posibles errores, como un ID malformado
        raise HTTPException(status_code=400, detail=f"userId not exist: {e}")
    
    # Añadir el ID del usuario a la lista de participantes
    try:

        event.participants.append(userId)
        event.participants = list(set(event.participants))

    except Exception as e:

        raise HTTPException(status_code=400, detail=f"Invalid userId: {e}")

    # Actualizamos la fecha de actualizacion
    event_dict = event.model_dump()
    event_dict["updated_at"] = datetime.now(tz=timezone.utc)
    event_update = EventUpdate(**event_dict)
    
    # Actualizar el evento en la base de datos
    new_event = await update_event(eventId, event_update)

    # Actualizar el usuario para añadir el ID del evento a la lista de eventos participados
    await db.get_collection("users").update_one(

        {"_id": ObjectId(userId)},
        {"$addToSet": {"participating_events": ObjectId(new_event.id)}}

    )

    return {"message": "User added to event successfully"}

async def remove_user_from_event(eventId: str, userId: str) -> object:
    # Buscar el evento
    event = await get_event_by_id(eventId)

    # Verificar que el evento existe
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")

    # Verificar si el usuario es un participante
    if userId not in event.participants:
        raise HTTPException(status_code=400, detail="User is not a participant of this event")

    try:
        # Convertir el user_id a ObjectId
        object_id = ObjectId(userId)

        # Buscar el usuario en la colección "users"
        user = await db.get_collection("users").find_one({"_id": object_id})
        
        # Verificar que el usuario existe
        if not user:
            raise HTTPException(status_code=400, detail="User does not exist")

    except Exception as e:
        # Manejar posibles errores, como un ID malformado
        raise HTTPException(status_code=400, detail=f"Invalid userId: {e}")
    
    # Eliminar el ID del usuario de la lista de participantes
    try:
        event.participants.remove(userId)
    except ValueError:
        # Manejar el caso si el usuario no estaba en la lista (aunque debería haber sido verificado antes)
        raise HTTPException(status_code=400, detail="User is not a participant of this event")

    # Actualizar la fecha de actualización
    event_dict = event.model_dump()
    event_dict["updated_at"] = datetime.now(tz=timezone.utc)
    event_update = EventUpdate(**event_dict)

    # Actualizar el evento en la base de datos
    new_event = await update_event(eventId, event_update)

    # Actualizar el usuario para eliminar el ID del evento de la lista de eventos participados
    await db.get_collection("users").update_one(
        {"_id": ObjectId(userId)},
        {"$pull": {"participating_events": ObjectId(new_event.id)}}
    )

    return {"message": "User removed from event successfully"}