from models import UserModel, EventModel, GroupModel
from schemas import UserCreate, UserUpdate, UserRead
from database import db  # Conexión a la base de datos
from bson import ObjectId
from typing import List
from datetime import datetime, timezone
from fastapi import HTTPException, status
from services import auth_services

# El archivo client_services.py contiene la lógica de negocio de la aplicación. 
# Este archivo actúa como una capa de servicio que encapsula la lógica para interactuar con los modelos y esquemas.

# Servicio para registrar usuarios
async def register_user(user_data: UserCreate) -> UserRead:
    
    # Verificar si el correo ya existe
    if await db.get_collection("users").find_one({"email": user_data.email}):
        raise HTTPException(status_code=400, detail="Email already registered")

    # Hashing de la contraseña antes de almacenarla
    hashed_password = auth_services.hash_password(user_data.password)

    # Transformacion a dict
    user_dict = user_data.model_dump()

    # Insertar la fecha de creación actual en UTC
    user_dict["created_at"] = datetime.now(tz=timezone.utc)

    # Insertar contrasena
    user_dict['password'] = hashed_password  # Actualizar la contraseña hasheada

    # Insertar el nuevo usuario en la base de datos
    new_user = await db.get_collection("users").insert_one(user_dict)
    user_dict['id'] = str(new_user.inserted_id)
    del user_dict['_id']  # Eliminar _id antes de devolverlo al usuario
    del user_dict['password']  # No devolver la contraseña

    return UserRead(**user_dict)

async def update_user(user_update: UserUpdate, current_user: dict) -> UserRead:

    current_user_dict = current_user.model_dump()
    user_id = current_user_dict['id']

    user_dict = user_update.model_dump()
    
    filtered_user_dict = {k: v for k, v in user_dict.items() if v not in [None, "", [], {}]}

    if not filtered_user_dict:
        raise HTTPException(status_code=400, detail="No fields to update")

    result = await db.get_collection("users").update_one(
        {"_id": ObjectId(user_id)}, {"$set": filtered_user_dict}
    )

    if result.matched_count == 1:
        return await get_user_by_id(user_id)

    return None

async def delete_user(current_user: dict) -> dict:

    current_user_dict = current_user.model_dump()
    user_id = current_user_dict['id']
    
    # Primero, verifica si el usuario existe
    existing_user = await db.get_collection("users").find_one({"_id": ObjectId(user_id)})
    if not existing_user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    # Si existe, procede a eliminarlo
    result = await db.get_collection("users").delete_one({"_id": ObjectId(user_id)})
    if result.deleted_count == 1:
        return {"message": "User successfully deleted"}
    else:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="User deletion failed")

# Servicio para listar todos los usuarios
async def list_users() -> List[UserRead]:
    
    cursor = db.get_collection("users").find()
    users = [UserModel.from_db(user) async for user in cursor]
    return users

# Servicio para obtener un usuario por su ID
async def get_user_by_id(user_id: str) -> UserRead:

    # Buscar el usuario en la base de datos usando el ID
    user_data = await db.get_collection("users").find_one({"_id": ObjectId(user_id)})
    
    # Si no se encuentra el usuario, retornar None
    if user_data is None:
        return None
    
    # Convertir el documento de la base de datos a un modelo de usuario
    return UserModel.from_db(user_data)

async def get_user_by_email(user_email: str) -> UserRead:

    # Buscar el usuario en la base de datos usando el ID
    user_data = await db.get_collection("users").find_one({"email": user_email})
    
    # Si no se encuentra el usuario, retornar None
    if user_data is None:
        return None
    
    # Convertir el documento de la base de datos a un modelo de usuario
    return UserModel.from_db(user_data)

# Servicio para mostrar los eventos en los que participa un usuario
async def get_user_participating_events(user_id: str) -> List[EventModel]:
    cursor = db.get_collection("events").find({"participants": ObjectId(user_id)})
    events = await cursor.to_list(length=100)
    return [EventModel.from_db(event) for event in events]

# Servicio para mostrar los eventos creados por un usuario
async def get_user_created_events(user_id: str) -> List[EventModel]:
    cursor = db.get_collection("events").find({"creator_id": ObjectId(user_id)})
    events = await cursor.to_list(length=100)
    return [EventModel.from_db(event) for event in events]

# Servicio para mostrar los grupos en los que esta un usuario
async def get_user_groups(user_id: str) -> List[GroupModel]:
    cursor = db.get_collection("groups").find({"members": ObjectId(user_id)})
    groups = await cursor.to_list(length=100)
    return [GroupModel.from_db(group) for group in groups]








