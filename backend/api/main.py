from fastapi import FastAPI
from contextlib import asynccontextmanager
from logger import logging
from backend.api.routes import chat_endpoint, data_endpoints
from rag.vector_store.embeddings import EmbeddingManager

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup logic
    try:
        app.state.embedding_manager = EmbeddingManager()
    except Exception as e:
        logging.error(f"Error while app startup: {e}")
        raise
    
    print("App started")
    
    
    
    yield  # <-- app runs here

    # hutdown logic
    print("Shutting down")

app = FastAPI(
    title="DB Query API",
    description="Query database through API",
    version="1.0",
    lifespan=lifespan
)

# Register routes
app.include_router(data_endpoints.router, prefix="/api", tags=["Query Database"])
app.include_router(chat_endpoint.router, prefix="/api", tags=["Chat"])


@app.get("/")
def root():
    return {"message": "Query Database API is running"}

