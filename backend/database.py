from motor.motor_asyncio import AsyncIOMotorClient
from pymongo.collection import Collection
from typing import Dict

# Clase para gestionar la conexión con MongoDB
class Database:
    def __init__(self, db_url: str):
        self.client = AsyncIOMotorClient(db_url)  # Conexión asíncrona a MongoDB
        self.database = self.client["Cluster0"]  # Seleccionamos la base de datos

    def get_collection(self, name: str) -> Collection:
        return self.database[name]  # Retornamos la colección solicitada

# Instanciamos la clase Database con la URL de conexión a MongoDB Atlas
db = Database('mongodb+srv://alblinmah:oJHDakVTiSN1Hm2g@cluster0.i4bozif.mongodb.net/')

# from motor.motor_asyncio import AsyncIOMotorClient
# from pymongo.collection import Collection

# class Database:
#     def __init__(self, db_url: str):
#         self.client = AsyncIOMotorClient(db_url)
#         self.database = self.client["Cluster0"]  # Cambia 'Cluster0' por el nombre real de tu base de datos
#         self.users = self.database["users"]  # Acceso directo a la colección 'users'
#         self.events = self.database["events"]  # Acceso directo a la colección 'events'

# # Instanciamos la clase Database con la URL de conexión a MongoDB Atlas
# db = Database('mongodb+srv://alblinmah:oJHDakVTiSN1Hm2g@cluster0.i4bozif.mongodb.net/')



