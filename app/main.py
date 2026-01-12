from fastapi import FastAPI
from app.models import User, Todo
from app.core.database import engine, Base
from app.api.v1 import api_router

# Create database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="FastAPI Todo API",
    description="A well-structured FastAPI application with user authentication and todo management",
    version="1.0.0"
)

from fastapi.middleware.cors import CORSMiddleware

origins = [
    "http://localhost:5173",
    "http://localhost:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API router
app.include_router(api_router)

@app.get("/")
def read_root():
    return {"message": "Welcome to the FastAPI Todo API"}

from fastapi.openapi.utils import get_openapi

# Override OpenAPI to avoid recursion
def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    
    app.openapi_schema = get_openapi(
        title=app.title,
        version=app.version,
        description=app.description,
        routes=app.routes,
    )
    return app.openapi_schema

app.openapi = custom_openapi
