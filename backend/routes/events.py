from fastapi import APIRouter, HTTPException, Depends
from schemas import EventCreate, EventRead, EventUpdate
from services import event_services # Servicio de eventos
from models import EventModel
from typing import List
from bson import ObjectId

router = APIRouter()

# Ruta para crear un nuevo evento
@router.post("/users/{user_id}/create_event", response_model=EventRead, status_code=201)
async def create_event(user_id: str, event: EventCreate):
    new_event = await event_services.create_event(user_id, event)
    return new_event

# Ruta para obtener un evento por su ID
@router.get("/events/{event_id}", response_model=EventRead)
async def read_event(event_id: str):
    event = await event_services.get_event_by_id(event_id)
    if event is None:
        raise HTTPException(status_code=404, detail="Event not found")
    return event

# Ruta para obtener eventos por ID de su creador
@router.get("/users/{user_id}/events/", response_model=List[EventRead])
async def read_event(user_id: str):
    events = await event_services.get_events_by_user_id(user_id)
    print(events)
    if events is None:
        raise HTTPException(status_code=404, detail="No events created by this user")
    return events

# Ruta para actualizar un evento por su ID
@router.put("/events/{event_id}", response_model=EventRead)
async def update_event(event_id: str, event: EventUpdate):
    updated_event = await event_services.update_event(event_id, event)
    if updated_event is None:
        raise HTTPException(status_code=404, detail="Event not found")
    return updated_event

# Ruta para obtener una lista de todos los eventos
@router.get("/events/", response_model=List[EventRead])
async def list_events():
    events = await event_services.list_events()
    return events

# Ruta para anadir a un usuario a un evento
@router.post("/events/{eventId}/participants/{userId}", response_model = EventRead)
async def add_user_to_event(eventId: str, userId: str):
    # Convertir los IDs a ObjectId
    # Buscar el evento
    event = await event_services.get_event_by_id(eventId)
    
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")

    # Verificar si el usuario ya es un participante
    if userId in event.participants:
        raise HTTPException(status_code=400, detail="User already added to this event")

    # Añadir el ID del usuario a la lista de participantes
    try:
        # Intentar convertir userId a ObjectId y añadirlo a la lista de participantes
        event.participants.append(ObjectId(userId))
    except Exception as e:
        # Si falla, lanzar una excepción HTTP con el estado 400 Bad Request
        raise HTTPException(status_code=400, detail=f"Invalid userId: {e}")


    print(event)

    event_dict = event.model_dump()

    event_update = EventUpdate(**event_dict)

    print(event_update)
    
    # Actualizar el evento en la base de datos
    await event_services.update_event(eventId, event_update)
    
    return event
