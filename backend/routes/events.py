# Importamos las librerías necesarias
from fastapi import APIRouter, HTTPException
from database import db
from models import Event
from schemas import EventCreate, EventResponse
from bson import ObjectId

router = APIRouter()  # Creamos un enrutador para las rutas de eventos

# Función auxiliar para convertir ObjectId a string
def objectid_to_str(obj_id: ObjectId) -> str:
    return str(obj_id)

# Ruta para crear un evento
@router.post("/events/", response_model=EventResponse)
async def create_event(event: EventCreate):
    # Convertimos el evento a un diccionario para insertarlo en MongoDB
    event_dict = event.model_dump()
    result = await db.get_collection("events").insert_one(event_dict)  # Insertamos el evento
    event_id = result.inserted_id  # Obtenemos el ID del documento insertado
    event_data = await db.get_collection("events").find_one({"_id": event_id})  # Obtenemos el documento insertado
    return EventResponse(**event_data, id=objectid_to_str(event_data["_id"]))  # Retornamos la respuesta

# Ruta para leer un evento por ID
@router.get("/events/{event_id}", response_model=EventResponse)
async def read_event(event_id: str):
    event = await db.get_collection("events").find_one({"_id": ObjectId(event_id)})  # Buscamos el evento por ID
    if event is None:
        raise HTTPException(status_code=404, detail="Event not found")  # Si no se encuentra el evento, lanzamos una excepción
    return EventResponse(**event, id=objectid_to_str(event["_id"]))  # Retornamos el evento encontrado

# Ruta para actualizar un evento por ID
@router.put("/events/{event_id}", response_model=EventResponse)
async def update_event(event_id: str, event: EventCreate):
    updated_event = await db.get_collection("events").update_one(
        {"_id": ObjectId(event_id)},
        {"$set": event.model_dump()}  # Actualizamos el evento con los nuevos datos
    )
    if updated_event.matched_count == 0:
        raise HTTPException(status_code=404, detail="Event not found")  # Si no se encuentra el evento, lanzamos una excepción
    event_data = await db.get_collection("events").find_one({"_id": ObjectId(event_id)})  # Obtenemos el evento actualizado
    return EventResponse(**event_data, id=objectid_to_str(event_data["_id"]))  # Retornamos el evento actualizado

# Ruta para eliminar un evento por ID
@router.delete("/events/{event_id}", response_model=dict)
async def delete_event(event_id: str):
    result = await db.get_collection("events").delete_one({"_id": ObjectId(event_id)})  # Eliminamos el evento por ID
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Event not found")  # Si no se encuentra el evento, lanzamos una excepción
    return {"status": "success", "message": "Event deleted"}  # Retornamos un mensaje de éxito
