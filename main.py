from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.adapters.api.order_router import router as order_router
from app.adapters.models.sql.base import Base
from app.adapters.models.sql.session import engine
from app.config import settings

# Create database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Orders Service API")

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(
    order_router,
    prefix=f"{settings.API_PREFIX}/orders",
    tags=["orders"],
)


@app.get("/", tags=["health"])
def health_check():
    return {"status": "ok", "service": "orders-service"} 