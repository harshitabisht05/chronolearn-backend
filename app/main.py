from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routes import playlists, calendar, auth
from app import models, database

app = FastAPI()

# CORS setup — adjust for your frontend domain
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Replace "*" with ["http://localhost:3000"] in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register all API routes
app.include_router(auth.router)
app.include_router(playlists.router)
app.include_router(calendar.router)

@app.get("/")
def read_root():
    return {"message": "YouTube Study Planner API is running"}
