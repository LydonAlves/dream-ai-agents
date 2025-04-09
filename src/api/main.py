from fastapi import FastAPI
from src.api.routes import router
from fastapi.middleware.cors import CORSMiddleware

# This is the entry point for the API application

# Creates an instance of the FastAPI application. Shown when I test on webpage
app = FastAPI(title="Dream AI Interpreter")

# Adds the routes from router.py to the main FastAPI. Modular approach: keeps code clean
app.include_router(router)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # or limit to ["http://192.168.0.16"] in prod
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
