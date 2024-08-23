from models import GroupModel
from schemas import GroupCreate, GroupUpdate
from database import db  # Conexión a la base de datos
from bson import ObjectId
from typing import List
from fastapi import HTTPException
from datetime import datetime, timezone

# El archivo group_services.py contiene la lógica de negocio de la aplicación. 
# Este archivo actúa como una capa de servicio que encapsula la lógica para interactuar con los modelos y esquemas.

# Servicio para crear un nuevo groupo
async def create_group(user_id: str, group: GroupCreate) -> GroupModel:
    group_dict = group.model_dump()
    group_dict["creator_id"] = ObjectId(user_id)
    group_dict["created_at"] = datetime.now(tz=timezone.utc)
    group_dict["members"] = [ObjectId(user_id)] 

    # Crear el groupo en la base de datos
    new_group = await db.get_collection("groups").insert_one(group_dict)
    group_dict["id"] = str(new_group.inserted_id)
    group_dict["creator_id"] = str(user_id)
    group_dict["members"] = [str(member_id) for member_id in group_dict["members"]]
    group_dict.pop("_id")    
    
    # Actualizar el usuario para añadir el ID del groupo a la lista de groupos creados
    result = await db.get_collection("users").update_one(
        {"_id": ObjectId(user_id)},
        {"$addToSet": {"created_groups": new_group.inserted_id}}
    )
    
    # Verificar si la actualización del usuario fue exitosa
    if result.modified_count != 1:
        raise HTTPException(status_code=500, detail="Error updating the user")
    
    return GroupModel(**group_dict)

# Servicio para obtener un grupo por su ID
async def get_group_by_id(group_id: str) -> GroupModel:

    # Recupera datos de la base de datos
    db_data = await db.get_collection("groups").find_one({"_id": ObjectId(group_id)})
    if db_data:
        # Convierte datos de la base de datos a un modelo de Pydantic
        return GroupModel.from_db(db_data)
    
    raise HTTPException(status_code=404, detail="Group not found")

# Servicio para listar todos los grupos
async def list_groups() -> List[GroupModel]:

    try:
        cursor = db.get_collection("groups").find()
        groups = []
        async for db_group in cursor:
            groups.append(GroupModel.from_db(db_group))

        return groups
    
    except Exception as e:
        raise HTTPException(status_code=500, detail="Error retrieving events")
    
# Servicio para actualizar un grupo existente
async def update_group(group_id: str, group: GroupUpdate) -> GroupModel:

    # Primero se transforma el modelo de actualización a un formato de base de datos
    group_dict = group.model_dump()

    # Filtrar valores nulos, vacíos y listas vacías
    filtered_group_dict = {k: v for k, v in group_dict.items() if v not in [None, "", [], {}]}

    filtered_group_dict["updated_at"] = datetime.now(tz=timezone.utc)

    # Verificar si hay campos para actualizar
    if not filtered_group_dict:
        raise HTTPException(status_code=400, detail="No fields to update")

    # Actualizar el grupo en la base de datos
    result = await db.get_collection("groups").update_one(
        {"_id": ObjectId(group_id)}, {"$set": filtered_group_dict}
    )

    # Verificar si la actualización fue exitosa
    if result.matched_count == 1:
        # Obtener y retornar el grupo actualizado
        updated_group = await db.get_collection("groups").find_one({"_id": ObjectId(group_id)})
        if updated_group:
            return GroupModel.from_db(updated_group)
    
    raise HTTPException(status_code=404, detail="Group not found")
