from fastapi import FastAPI
from routes import test_connection, events, users

app = FastAPI()

app.include_router(events.router)
app.include_router(users.router)
app.include_router(test_connection.router)
