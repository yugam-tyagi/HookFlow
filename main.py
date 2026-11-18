from contextlib import asynccontextmanager
from fastapi import FastAPI
from database import check_database_connection
from routers.clients import router as client_router
from routers.api_keys import router as api_key_router
from routers.webhook_endpoints import router as webhook_endpoint_router
from routers.events import router as event_router

@asynccontextmanager
async def lifespan(app: FastAPI):
    check_database_connection()
    yield


app = FastAPI(
    title="HookFlow",
    description="Reliable Webhook Delivery Platform",
    version="1.0.0",
    lifespan=lifespan
)

app.include_router(client_router)
app.include_router(api_key_router)
app.include_router(webhook_endpoint_router)
app.include_router(event_router)

@app.get("/health")
def health_check():
    return {
        "status": "UP",
        "service": "HookFlow"
    }
