from fastapi import FastAPI
from contextlib import asynccontextmanager
import uvicorn
from sqlalchemy import text
from utils.logger import setup_logging
from core.database import engine
from modules.chat import router as chat_router



logger = setup_logging()

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Connect to the database
    logger.info("Starting up application...")
    try:
        async with engine.begin() as conn:
            await conn.execute(text("SELECT 1"))
        logger.info("Database connection established and pool created.")
    except Exception as e:
        logger.error(f"Failed to connect to database: {e}")
        raise e
    
    yield
    
    # Shutdown: Close database connections
    logger.info("Shutting down application...")
    await engine.dispose()
    logger.info("Database connections closed.")

app = FastAPI(lifespan=lifespan)

app.include_router(chat_router)

@app.get("/")
def read_root():
    logger.info("Root endpoint called")
    return {"Hello": "World"}

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)