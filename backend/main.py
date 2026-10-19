from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.routers.chat_router import router as chat_router
from src.routers.document_router import router as document_router
from src.routers.conversation_router import router as conversation_router
from src.services.conversation_service import init_db


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Runs once when the application starts.
    init_db()

    yield

    # Runs when the application shuts down.
    # Add cleanup here later if needed.
    
app = FastAPI(title="AI Chatbot API", lifespan=lifespan)

# Allow our local React frontend to communicate with FastAPI.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

# @app.on_event("startup")
# def initialize_database():
#     init_db()
    
@app.get("/")
def home():
    return {
        "message": "Welcome to the AI Chatbot API!"
    }

@app.get("/health")
def health_check():
    return {
        "status": "healthy"
    }
    
app.include_router(chat_router)    
app.include_router(document_router)
app.include_router(conversation_router)