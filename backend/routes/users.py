from fastapi import APIRouter, HTTPException
from schemas import UserCreate, UserRead, UserUpdate
from models import EventModel, GroupModel
from services import user_services, event_services, group_services # Servicio de usuarios
from typing import List

router = APIRouter()

# Ruta para crear un nuevo usuario
@router.post("/users/", response_model=UserRead, status_code=201)
async def create_user(user: UserCreate):
    # Crear un nuevo usuario utilizando el servicio de usuarios
    new_user = await user_services.create_user(user)
    return new_user

# Ruta para obtener una lista de todos los usuarios
@router.get("/users/", response_model=List[UserRead])
async def list_users():
    # Obtener una lista de todos los usuarios utilizando el servicio de usuarios
    users = await user_services.list_users()
    return users

# Ruta para obtener un usuario por su ID
@router.get("/users/{user_id}", response_model=UserRead)
async def read_user(user_id: str):
    # Obtener un usuario por su ID utilizando el servicio de usuarios
    user = await user_services.get_user_by_id(user_id)
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return user

### Eventos

# Ruta para actualizar un usuario por su ID
@router.put("/users/{user_id}", response_model=UserRead)
async def update_user(user_id: str, user: UserUpdate):
    # Actualizar un usuario existente utilizando el servicio de usuarios
    updated_user = await user_services.update_user(user_id, user)
    if updated_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return updated_user

# Ruta para ver eventos en los que participa un usuario
@router.get("/users/{userId}/participating_events", response_model=List[EventModel])
async def get_participating_events(userId: str):
    events = await user_services.get_user_participating_events(userId)
    if not events:
        raise HTTPException(status_code=404, detail="No events found for this user")
    return events

# Ruta para ver eventos creados por un usuario
@router.get("/users/{userId}/created_events", response_model=List[EventModel])
async def get_created_events(userId: str):
    events = await user_services.get_user_created_events(userId)
    if not events:
        raise HTTPException(status_code=404, detail="No events found for this user")
    return events

# Ruta para anadir a un usuario a un evento
@router.post("/users/{userId}/participate/{eventId}/", response_model = object)
async def add_user_to_event(eventId: str, userId: str):
    event = await event_services.add_user_to_event(eventId, userId)
    return event

# Ruta para eliminar a un usuario a un evento
@router.delete("/users/{userId}/participate/{eventId}/", response_model = object)
async def remove_user_from_event(eventId: str, userId: str):
    event = await event_services.remove_user_from_event(eventId, userId)
    return event

### Grupos

# Ruta para ver grupos en los que participa un usuario
@router.get("/users/{userId}/groups", response_model=List[GroupModel])
async def get_participating_groups(userId: str):
    groups = await user_services.get_user_groups(userId)
    if not groups:
        raise HTTPException(status_code=404, detail="No groups found for this user")
    return groups

# Ruta para añadir a un usuario a un grupo
@router.post("/users/{userId}/join/{groupId}/", response_model=object)
async def add_user_to_group(groupId: str, userId: str):
    group = await group_services.add_user_to_group(groupId, userId)
    return group

# # Ruta para eliminar a un usuario de un grupo
# @router.delete("/users/{userId}/leave/{groupId}/", response_model=object)
# async def remove_user_from_group(groupId: str, userId: str):
#     group = await group_services.remove_user_from_group(groupId, userId)
#     return group



