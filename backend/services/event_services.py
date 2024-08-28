from models import EventModel
from schemas import EventCreate, EventUpdate, UserRead
from database import db  # Conexión a la base de datos
from bson import ObjectId
from typing import List
from fastapi import HTTPException, status
from datetime import datetime, timezone

# El archivo event_services.py contiene la lógica de negocio de la aplicación. 
# Este archivo actúa como una capa de servicio que encapsula la lógica para interactuar con los modelos y esquemas.

# Servicio para crear un nuevo evento
async def create_event(current_user: UserRead, event: EventCreate) -> EventModel:

    user_id = current_user.id

    # Primero, verifica si el usuario existe
    existing_user = await db.get_collection("users").find_one({"_id": ObjectId(user_id)})
    if not existing_user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    
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
    
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Event not found")

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
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="An error occurred while retrieving events.")
    
    
# Servicio para actualizar un evento existente
async def update_event(current_user: UserRead, event: EventUpdate, event_id: str) -> EventModel:
    # Buscar el evento para verificar que el usuario actual es el creador
    existing_event = await db.get_collection("events").find_one({"_id": ObjectId(event_id)})
    if not existing_event:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Event not found")
    
    if str(existing_event['creator_id']) != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to update this event")

    # Primero se transforma el modelo a modelo de database
    event_dict = event.to_db()
    print(event_dict)
    # Filtrar valores nulos, vacíos y listas vacías
    filtered_event_dict = {k: v for k, v in event_dict.items() if v not in [None, "", [], {}]}

    # Verificar si hay campos para actualizar
    if not filtered_event_dict:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No fields to update")

    filtered_event_dict["updated_at"] = datetime.now(tz=timezone.utc)
    
    # Actualizar el evento en la base de datos
    result = await db.get_collection("events").update_one(
        {"_id": ObjectId(event_id)}, {"$set": filtered_event_dict}
    )

    # Verificar si la actualización fue exitosa
    if result.matched_count == 1:
        # Obtener y retornar el evento actualizado
        return await get_event_by_id(event_id)
    
    return None

# Servicio para eliminar un evento
async def delete_event(current_user: UserRead, event_id: str) -> dict:
    # Buscar el evento en la base de datos para confirmar que el usuario actual es el creador
    event = await db.get_collection("events").find_one({"_id": ObjectId(event_id)})
    
    if not event:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Event not found")
    
    # Verificar si el usuario actual es el creador del evento
    if str(event['creator_id']) != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You are not authorized to delete this event")
    
    # Proceder a eliminar el evento si el usuario es el creador
    result = await db.get_collection("events").delete_one({"_id": ObjectId(event_id)})
    
    if result.deleted_count == 1:
        return {"message": "Event successfully deleted"}
    else:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="The event could not be deleted")


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

# Servicio para anadir un participante a un evento
async def add_user_to_event(eventId: str, current_user: UserRead) -> dict:
    
    userId = current_user.id

    # Buscar el evento
    event = await get_event_by_id(eventId)
    
    # Verificar que el evento existe
    if not event:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Event not found")
    
    # Verificar si se ha alcanzado el límite máximo de participantes
    if len(event.participants) >= event.max_participants:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Event is already full")

    # Verificar si el usuario ya es un participante
    if userId in event.participants:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="User already added to this event")
    
    # Añadir el ID del usuario a la lista de participantes
    updated_participants = list(set(event.participants + [userId]))

    # Preparar actualización del evento
    event_update_dict = {
        "participants": updated_participants,
        "updated_at": datetime.now(tz=timezone.utc)
    }

    # Actualizar el evento en la base de datos
    update_result = await db.get_collection("events").update_one(
        {"_id": ObjectId(eventId)},
        {"$set": event_update_dict}
    )

    if update_result.modified_count == 0:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to update event participants")

    # Actualizar el usuario para añadir el ID del evento a la lista de eventos participados
    user_update_result = await db.get_collection("users").update_one(
        {"_id": ObjectId(userId)},
        {"$addToSet": {"participating_events": ObjectId(eventId)}}
    )

    if user_update_result.modified_count == 0:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to update user's participating events")

    return {"message": "User successfully added to the event"}

# Servicio para eliminar un participante de un evento
async def remove_user_from_event(eventId: str, current_user: UserRead) -> dict:
    
    userId = current_user.id

    # Buscar el evento
    event = await get_event_by_id(eventId)

    # Verificar que el evento existe y el usuario es participante
    if not event:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Event not found")
    if userId not in event.participants:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="User is not a participant of this event")

    # Eliminar el ID del usuario de la lista de participantes
    updated_participants = [participant for participant in event.participants if participant != userId]

    # Preparar actualización del evento
    event_update_dict = {
        "participants": updated_participants,
        "updated_at": datetime.now(tz=timezone.utc)
    }

    # Actualizar el evento en la base de datos
    update_result = await db.get_collection("events").update_one(
        {"_id": ObjectId(eventId)},
        {"$set": event_update_dict}
    )

    if update_result.modified_count == 0:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to update event participants")

    # Actualizar el usuario para eliminar el ID del evento de la lista de eventos participados
    user_update_result = await db.get_collection("users").update_one(
        {"_id": ObjectId(userId)},
        {"$pull": {"participating_events": ObjectId(eventId)}}
    )

    if user_update_result.modified_count == 0:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to update user's participating events")

    return {"message": "User successfully removed from the event"}
