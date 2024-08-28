from fastapi import APIRouter, HTTPException, Depends
from schemas import EventCreate, EventRead, EventUpdate
from schemas import UserRead
from services import event_services, auth_services
from typing import List

router = APIRouter()

# Ruta para crear un nuevo evento
@router.post("/users/me/create_event", response_model=EventRead, status_code=201, tags = ["user-events"])
async def create_event(event: EventCreate, current_user: UserRead = Depends(auth_services.get_current_user)):
    return await event_services.create_event(current_user, event)
 
# Ruta para actualizar un evento por su ID
@router.put("/users/me/update_event/{event_id}", response_model=EventRead, tags = ["user-events"])
async def update_event(event_id:str, event: EventUpdate, current_user: UserRead = Depends(auth_services.get_current_user)):
    return await event_services.update_event(current_user, event, event_id)

# Ruta para eliminar un evento por su ID
@router.delete("/users/me/delete_event/{event_id}", response_model= dict, tags = ["user-events"])
async def delete_event(event_id:str, current_user: UserRead = Depends(auth_services.get_current_user)):
    return await event_services.delete_event(current_user, event_id)

# Ruta para obtener un evento por su ID
@router.get("/events/{event_id}", response_model=EventRead, tags = ["events"])
async def read_event(event_id: str):
    event = await event_services.get_event_by_id(event_id)
    if event is None:
        raise HTTPException(status_code=404, detail="Event not found")
    return event

# Ruta para obtener una lista de todos los eventos
@router.get("/events/", response_model=List[EventRead], tags = ["events"])
async def list_events():
    events = await event_services.list_events()
    return events




