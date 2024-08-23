from fastapi import FastAPI
from routes import groups, events, users

app = FastAPI()

app.include_router(users.router)
app.include_router(events.router)
app.include_router(groups.router)
