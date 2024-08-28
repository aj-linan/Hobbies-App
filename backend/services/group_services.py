from models import GroupModel
from schemas import GroupCreate, GroupUpdate, UserRead
from database import db  # Conexión a la base de datos
from bson import ObjectId
from typing import List
from fastapi import HTTPException,status
from datetime import datetime, timezone
from pymongo.errors import DuplicateKeyError


# El archivo group_services.py contiene la lógica de negocio de la aplicación. 
# Este archivo actúa como una capa de servicio que encapsula la lógica para interactuar con los modelos y esquemas.

# Servicio para crear un nuevo grupo
async def create_group(current_user: UserRead, group: GroupCreate) -> GroupModel:
    user_id = current_user.id

    # Comprobar si el usuario existe
    if not await db.get_collection("users").find_one({"_id": ObjectId(user_id)}):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    group_dict = group.model_dump()
    group_dict["creator_id"] = ObjectId(user_id)
    group_dict["created_at"] = datetime.now(tz=timezone.utc)
    group_dict["members"] = [ObjectId(user_id)]

    # Intentar crear el grupo en la base de datos
    try:
        new_group = await db.get_collection("groups").insert_one(group_dict)
        group_dict["id"] = str(new_group.inserted_id)
        group_dict["creator_id"] = str(user_id)
        group_dict["members"] = [str(member_id) for member_id in group_dict["members"]]
        group_dict.pop("_id")

    except DuplicateKeyError:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Group with similar attributes already exists")

    # Actualizar el usuario para añadir el ID del grupo a la lista de grupos creados
    result = await db.get_collection("users").update_one(
        {"_id": ObjectId(user_id)},
        {"$addToSet": {"created_groups": new_group.inserted_id}}
    )

    # Verificar si la actualización del usuario fue exitosa
    if result.modified_count != 1:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error updating the user")

    return GroupModel(**group_dict)

# Servicio para obtener un grupo por su ID
async def get_group_by_id(group_id: str) -> GroupModel:

    # Recupera datos de la base de datos
    db_data = await db.get_collection("groups").find_one({"_id": ObjectId(group_id)})
    if db_data:
        # Convierte datos de la base de datos a un modelo de Pydantic
        return GroupModel.from_db(db_data)
    
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Group not found")

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
async def update_group(current_user: UserRead, group_update: GroupUpdate, group_id: str) -> GroupModel:

    # Buscar el grupo para verificar que el usuario actual es el creador
    existing_group = await db.get_collection("groups").find_one({"_id": ObjectId(group_id)})
    if not existing_group:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Group not found")
    
    print(existing_group)
    if str(existing_group['creator_id']) != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to update this group")

    # Primero se transforma el modelo a modelo de database
    group_dict = group_update.to_db()
    print(group_dict)
    # Filtrar valores nulos, vacíos y listas vacías
    filtered_group_dict = {k: v for k, v in group_dict.items() if v not in [None, "", [], {}]}

    # Verificar si hay campos para actualizar
    if not filtered_group_dict:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No fields to update")

    filtered_group_dict["updated_at"] = datetime.now(tz=timezone.utc)
    
    # Actualizar el grupo en la base de datos
    result = await db.get_collection("groups").update_one(
        {"_id": ObjectId(group_id)}, {"$set": filtered_group_dict}
    )

    # Verificar si la actualización fue exitosa
    if result.matched_count == 1:
        # Obtener y retornar el grupo actualizado
        return await get_group_by_id(group_id)
    
    return None


# Servicio para eliminar un grupo
async def delete_group(current_user: UserRead, group_id: str) -> dict:
    # Buscar el grupo en la base de datos para confirmar que el usuario actual es el creador
    group = await db.get_collection("groups").find_one({"_id": ObjectId(group_id)})
    
    if not group:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Group not found")
    
    # Verificar si el usuario actual es el creador del grupo
    if str(group['creator_id']) != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You are not authorized to delete this group")
    
    # Proceder a eliminar el grupo si el usuario es el creador
    result = await db.get_collection("groups").delete_one({"_id": ObjectId(group_id)})
    
    if result.deleted_count == 1:
        return {"message": "Group successfully deleted"}
    else:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="The group could not be deleted")

# Servicio para anadir un participante a un grupo
async def add_user_to_group(groupId: str, current_user: UserRead) -> dict:
    
    userId = current_user.id

    # Buscar el grupo
    group = await get_group_by_id(groupId)
    
    # Verificar que el grupo existe
    if not group:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Group not found")
    
    # Verificar si se ha alcanzado el límite máximo de participantes
    if len(group.members) >= group.max_participants:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Group is already full")

    # Verificar si el usuario ya es un participante
    if userId in group.members:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="User already added to this group")
    
    # Añadir el ID del usuario a la lista de participantes
    updated_members = list(set(group.members + [userId]))

    # Preparar actualización del grupo
    group_update_dict = {
        "members": updated_members,
        "updated_at": datetime.now(tz=timezone.utc)
    }

    # Actualizar el grupo en la base de datos
    update_result = await db.get_collection("groups").update_one(
        {"_id": ObjectId(groupId)},
        {"$set": group_update_dict}
    )

    if update_result.modified_count == 0:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to update group members")

    # Actualizar el usuario para añadir el ID del grupo a la lista de grupos participados
    user_update_result = await db.get_collection("users").update_one(
        {"_id": ObjectId(userId)},
        {"$addToSet": {"groups": ObjectId(groupId)}}
    )

    if user_update_result.modified_count == 0:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to update user's participating groups")

    return {"message": "User successfully added to the group"}

# Servicio para eliminar un participante de un grupo
async def remove_user_from_group(groupId: str, current_user: UserRead) -> dict:
    
    userId = current_user.id

    # Buscar el grupo
    group = await get_group_by_id(groupId)

    # Verificar que el grupo existe y el usuario es participante
    if not group:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Group not found")
    if userId not in group.members:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="User is not a participant of this group")

    # Eliminar el ID del usuario de la lista de participantes
    updated_members = [participant for participant in group.members if participant != userId]

    # Preparar actualización del grupo
    group_update_dict = {
        "members": updated_members,
        "updated_at": datetime.now(tz=timezone.utc)
    }

    # Actualizar el grupo en la base de datos
    update_result = await db.get_collection("groups").update_one(
        {"_id": ObjectId(groupId)},
        {"$set": group_update_dict}
    )

    if update_result.modified_count == 0:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to update group members")

    # Actualizar el usuario para eliminar el ID del grupo de la lista de grupos participados
    user_update_result = await db.get_collection("users").update_one(
        {"_id": ObjectId(userId)},
        {"$pull": {"groups": ObjectId(groupId)}}
    )

    if user_update_result.modified_count == 0:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to update user's participating groups")

    return {"message": "User successfully removed from the group"}
