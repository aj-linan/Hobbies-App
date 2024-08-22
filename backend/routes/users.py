from fastapi import APIRouter, HTTPException, Depends
from schemas import UserCreate, UserRead, UserUpdate
from models import UserModel
from services import user_services  # Servicio de usuarios
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

# Ruta para actualizar un usuario por su ID
@router.put("/users/{user_id}", response_model=UserRead)
async def update_user(user_id: str, user: UserUpdate):
    # Actualizar un usuario existente utilizando el servicio de usuarios
    updated_user = await user_services.update_user(user_id, user)
    if updated_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return updated_user



