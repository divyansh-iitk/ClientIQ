from fastapi import FastAPI
from contextlib import asynccontextmanager
from backend.api.routes import endpoints

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup logic
    
    
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
app.include_router(endpoints.router, prefix="/api", tags=["Query"])


@app.get("/")
def root():
    return {"message": "Query Database API is running"}

