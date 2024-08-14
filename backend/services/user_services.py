from models import UserModel
from schemas import UserCreate, UserUpdate
from database import db  # Conexión a la base de datos
from bson import ObjectId
from typing import List

# El archivo client_services.py contiene la lógica de negocio de la aplicación. 
# Este archivo actúa como una capa de servicio que encapsula la lógica para interactuar con los modelos y esquemas.

# Servicio para crear un nuevo usuario
async def create_user(user: UserCreate) -> UserModel:
    # Encriptar la contraseña aquí antes de guardarla
    user_dict = user.model_dump()
    user_dict["password"] = hash_password(user_dict.pop("password"))
    # Insertar el nuevo usuario en la base de datos
    new_user = await db.get_collection("users").insert_one(user_dict)
    user_dict["id"] = str(new_user.inserted_id)
    user_dict.pop("_id")
    print(user_dict)
    return UserModel(**user_dict)

# Servicio para obtener un usuario por su ID
async def get_user_by_id(user_id: str) -> UserModel:
    user = await db.get_collection("users").find_one({"_id": ObjectId(user_id)})
    if user:
        return UserModel(**user)
    return None

# Servicio para actualizar un usuario existente
async def update_user(user_id: str, user: UserUpdate) -> UserModel:
    user_dict = {k: v for k, v in user.model_dump().items() if v is not None}
    if "password" in user_dict:
        user_dict["hashed_password"] = hash_password(user_dict.pop("password"))
    result = await db.get_collection("users").update_one(
        {"_id": ObjectId(user_id)}, {"$set": user_dict}
    )
    if result.matched_count == 1:
        return await get_user_by_id(user_id)
    return None

# Servicio para listar todos los usuarios
async def list_users() -> List[UserModel]:
    users = await db.get_collection("users").find().to_list(length=100)
    return [UserModel(**user) for user in users]

# Función auxiliar para encriptar la contraseña (simplificada)
def hash_password(password: str) -> str:
    # Aquí podrías usar una librería como bcrypt
    return "hashed_" + password  # Esto es solo un ejemplo simplificado