from models import UserModel, EventModel, GroupModel
from schemas import UserCreate, UserUpdate, UserRead
from database import db  # Conexión a la base de datos
from bson import ObjectId
from typing import List
from datetime import datetime, timezone
from fastapi import HTTPException

# El archivo client_services.py contiene la lógica de negocio de la aplicación. 
# Este archivo actúa como una capa de servicio que encapsula la lógica para interactuar con los modelos y esquemas.

# Servicio para crear un nuevo usuario
async def create_user(user: UserCreate) -> UserModel:
    
    # Encriptar la contraseña aquí antes de guardarla
    user_dict = user.model_dump()  # Utiliza .dict() en lugar de .model_dump()

     # Verificar si ya existe un usuario con el mismo correo electrónico
    existing_user = await db.get_collection('users').find_one({"email": user_dict['email']})
    
    if existing_user:
        raise HTTPException(status_code=409, detail="A user with this email already exists")
    
    # Añadir la fecha de creación actual en UTC
    user_dict["created_at"] = datetime.now(tz=timezone.utc)
    
    # Encriptar la contraseña
    user_dict["password"] = hash_password(user_dict.pop("password"))
    
    # Insertar el nuevo usuario en la base de datos
    new_user = await db.get_collection("users").insert_one(user_dict)
    user_dict["id"] = str(new_user.inserted_id)
    user_dict.pop("_id")  # Eliminar el campo _id si existe
    
    return UserModel(**user_dict)

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

# Servicio para actualizar un usuario existente
async def update_user(user_id: str, user_update: UserUpdate) -> UserRead:

    # Convertir el modelo a diccionario y filtrar campos nulos
    user_dict = user_update.model_dump()

    # Filtrar valores nulos, vacíos y listas vacías
    filtered_user_dict = {k: v for k, v in user_dict.items() if v not in [None, "", [], {}]}

    # Verificar si hay campos para actualizar
    if not filtered_user_dict:
        raise HTTPException(status_code=400, detail="No fields to update")

    # Actualizar el usuario en la base de datos
    result = await db.get_collection("users").update_one(
        {"_id": ObjectId(user_id)}, {"$set": filtered_user_dict}
    )

    # Verificar si la actualización fue exitosa
    if result.matched_count == 1:
        # Obtener y retornar el usuario actualizado
        return await get_user_by_id(user_id)
    return None

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

# Función auxiliar para encriptar la contraseña (simplificada)
def hash_password(password: str) -> str:
    # Aquí podrías usar una librería como bcrypt
    return "hashed_" + password  # Esto es solo un ejemplo simplificado