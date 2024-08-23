from fastapi import APIRouter, HTTPException
from schemas import GroupCreate, GroupRead, GroupUpdate
from models import GroupModel
from services import group_services  # Servicio de usuarios
from typing import List

router = APIRouter()

# Ruta para crear un nuevo grupo
@router.post("/users/{user_id}/create_group", response_model=GroupRead, status_code=201)
async def create_group(user_id: str, group: GroupCreate):
    new_group = await group_services.create_group(user_id, group)
    return new_group

# Ruta para obtener un grupo por su ID
@router.get("/groups/{group_id}", response_model=GroupRead)
async def read_group(group_id: str):
    event = await group_services.get_group_by_id(group_id)
    if event is None:
        raise HTTPException(status_code=404, detail="Group not found")
    return event

# Ruta para actualizar un grupo por su ID
@router.put("/groups/{group_id}", response_model=GroupRead)
async def update_group(group_id: str, event: GroupUpdate):
    print(group_id)
    updated_group = await group_services.update_group(group_id, event)
    if updated_group is None:
        raise HTTPException(status_code=404, detail="Group not found")
    return updated_group

# Ruta para obtener una lista de todos los grupos
@router.get("/groups/", response_model=List[GroupRead])
async def list_groups():
    group = await group_services.list_groups()
    return group