from models import GroupModel
from schemas import GroupCreate, GroupUpdate
from database import db  # Conexión a la base de datos
from bson import ObjectId
from typing import List
from fastapi import HTTPException
from datetime import datetime, timezone

# El archivo group_services.py contiene la lógica de negocio de la aplicación. 
# Este archivo actúa como una capa de servicio que encapsula la lógica para interactuar con los modelos y esquemas.

# Servicio para crear un nuevo grupo
async def create_group(user_id: str, group: GroupCreate) -> GroupModel:
    group_dict = group.model_dump()
    group_dict["creator_id"] = ObjectId(user_id)
    group_dict["created_at"] = datetime.now(tz=timezone.utc)
    group_dict["members"] = [ObjectId(user_id)] 

    # Crear el grupo en la base de datos
    new_group = await db.get_collection("groups").insert_one(group_dict)
    group_dict["id"] = str(new_group.inserted_id)
    group_dict["creator_id"] = str(user_id)
    group_dict["members"] = [str(member_id) for member_id in group_dict["members"]]
    group_dict.pop("_id")    
    
    # Actualizar el usuario para añadir el ID del grupo a la lista de grupos creados
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
        raise HTTPException(status_code=500, detail="Error retrieving groups")
    
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


async def add_user_to_group(groupId: str, userId: str) -> dict:
    # Buscar el grupo
    group = await get_group_by_id(groupId)
    
    # Verificar que el grupo existe
    if not group:
        raise HTTPException(status_code=404, detail="Group not found")
    
    # Verificar que el grupo existe
    if group.is_private:
        raise HTTPException(status_code=404, detail="Group not found")
    
     # Verificar si se ha alcanzado el límite máximo de participantes
    if len(group.members) >= group.max_participants:
        raise HTTPException(status_code=400, detail="Group is full")

    # Verificar si el usuario ya es un participante
    if userId in group.members:
        raise HTTPException(status_code=400, detail="User already in this group")
    
    try:
        # Convertir el user_id a ObjectId
        object_id = ObjectId(userId)

        # Buscar el usuario en la colección "users"
        await db.get_collection("users").find_one({"_id": object_id})
    
    except Exception as e:
        # Manejar posibles errores, como un ID malformado
        raise HTTPException(status_code=400, detail=f"userId not exist: {e}")
    
    # Añadir el ID del usuario a la lista de participantes
    try:

        group.members.append(userId)
        group.members = list(set(group.members))

    except Exception as e:

        raise HTTPException(status_code=400, detail=f"Invalid userId: {e}")

    # Actualizamos la fecha de actualizacion
    group_dict = group.model_dump()
    group_dict["updated_at"] = datetime.now(tz=timezone.utc)
    group_update = GroupUpdate(**group_dict)
    
    # Actualizar el grupo en la base de datos
    new_group = await update_group(groupId, group_update)

    # Actualizar el usuario para añadir el ID del grupo a la lista de grupos participados
    await db.get_collection("users").update_one(

        {"_id": ObjectId(userId)},
        {"$addToSet": {"participating_groups": ObjectId(new_group.id)}}

    )

    return {"message": "User added to group successfully"}

async def remove_user_from_group(groupId: str, userId: str) -> object:
    # Buscar el grupo
    group = await get_group_by_id(groupId)

    # Verificar que el grupo existe
    if not group:
        raise HTTPException(status_code=404, detail="Event not found")

    # Verificar si el usuario es un participante
    if userId not in group.members:
        raise HTTPException(status_code=400, detail="User is not a participant of this group")

    try:
        # Convertir el user_id a ObjectId
        object_id = ObjectId(userId)

        # Buscar el usuario en la colección "users"
        user = await db.get_collection("users").find_one({"_id": object_id})
        
        # Verificar que el usuario existe
        if not user:
            raise HTTPException(status_code=400, detail="User does not exist")

    except Exception as e:
        # Manejar posibles errores, como un ID malformado
        raise HTTPException(status_code=400, detail=f"Invalid userId: {e}")
    
    # Eliminar el ID del usuario de la lista de participantes
    try:
        group.members.remove(userId)
    except ValueError:
        # Manejar el caso si el usuario no estaba en la lista (aunque debería haber sido verificado antes)
        raise HTTPException(status_code=400, detail="User is not a participant of this group")

    # Actualizar la fecha de actualización
    group_dict = group.model_dump()
    group_dict["updated_at"] = datetime.now(tz=timezone.utc)
    group_update = GroupUpdate(**group_dict)

    # Actualizar el grupo en la base de datos
    new_group = await update_group(groupId, group_update)

    # Actualizar el usuario para eliminar el ID del grupo de la lista de grupos participados
    await db.get_collection("users").update_one(
        {"_id": ObjectId(userId)},
        {"$pull": {"participating_groups": ObjectId(new_group.id)}}
    )

    return {"message": "User removed from group successfully"}
