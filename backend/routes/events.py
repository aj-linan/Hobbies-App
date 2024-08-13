from fastapi import APIRouter, HTTPException, Depends
from app.schemas import EventCreate, EventRead, EventUpdate
from app.services import event_service  # Servicio de eventos
from typing import List

router = APIRouter()

# Ruta para crear un nuevo evento
@router.post("/events/", response_model=EventRead)
async def create_event(event: EventCreate):
    new_event = await event_service.create_event(event)
    return new_event

# Ruta para obtener un evento por su ID
@router.get("/events/{event_id}", response_model=EventRead)
async def read_event(event_id: str):
    event = await event_service.get_event_by_id(event_id)
    if event is None:
        raise HTTPException(status_code=404, detail="Event not found")
    return event

# Ruta para actualizar un evento por su ID
@router.put("/events/{event_id}", response_model=EventRead)
async def update_event(event_id: str, event: EventUpdate):
    updated_event = await event_service.update_event(event_id, event)
    if updated_event is None:
        raise HTTPException(status_code=404, detail="Event not found")
    return updated_event

# Ruta para obtener una lista de todos los eventos
@router.get("/events/", response_model=List[EventRead])
async def list_events():
    events = await event_service.list_events()
    return events
