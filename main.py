from contextlib import asynccontextmanager

from fastapi import FastAPI

from database.mongodb import connect_to_mongodb, close_mongodb_connection
from routes import health, products, quotes


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan context manager for startup and shutdown events.
    """
    # Startup
    await connect_to_mongodb()
    yield
    # Shutdown
    await close_mongodb_connection()


app = FastAPI(lifespan=lifespan)

app.include_router(health.router)
app.include_router(products.router)
app.include_router(quotes.router)
