from fastapi import APIRouter, HTTPException, Depends
from schemas import GroupCreate, GroupRead, GroupUpdate, UserRead
from models import GroupModel
from services import group_services, auth_services # Servicio de usuarios
from typing import List

router = APIRouter()

# Ruta para crear un nuevo grupo
@router.post("/users/me/create_group", response_model=GroupRead, status_code=201, tags = ["user-groups"])
async def create_group(group: GroupCreate, current_user: UserRead = Depends(auth_services.get_current_user)):
    return await group_services.create_group(current_user, group)

# Ruta para actualizar un grupo por su ID
@router.put("/users/me/update_group/{group_id}", response_model=GroupRead, tags = ["user-groups"])
async def update_group(group_id:str, group: GroupUpdate, current_user: UserRead = Depends(auth_services.get_current_user)):
    return await group_services.update_group(current_user, group, group_id)

# Ruta para eliminar un grupo por su ID
@router.delete("/users/me/delete_group/{group_id}", response_model= dict, tags = ["user-groups"])
async def delete_group(group_id:str, current_user: UserRead = Depends(auth_services.get_current_user)):
    return await group_services.delete_group(current_user, group_id)

# Ruta para obtener un grupo por su ID
@router.get("/groups/{group_id}", response_model=GroupRead, tags = ["groups"])
async def read_group(group_id: str):
    return await group_services.get_group_by_id(group_id)

# Ruta para obtener una lista de todos los grupos
@router.get("/groups/", response_model=List[GroupRead], tags = ["groups"])
async def list_groups():
    return await group_services.list_groups()



