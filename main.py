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

import asyncio
from modules.personas.personal import Person

# if __name__ == "__main__":
#     uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)

async def main():
    print("----------------------------------------------------")
    print("人格测试模式")
    print("请输入你想要创建的人格描述 (例如: '一个活泼开朗，喜欢帮助别人的女孩'):")
    description = input("> ")

    print("\n正在生成人格档案，请稍候...")

    # For testing, we'll use a dummy name and gender.
    # The `if_original=True` is crucial for triggering the AI profiling.
    person = Person(name="Test Persona", gender="Female", if_original=True)
    await person.init_big_five_profile(description)

    print("\n----------------------------------------------------")
    print("人格档案生成完毕:")
    print(f"姓名: {person.name}")
    print(f"性别: {person.gender}")
    print(f"大五人格特质:")
    print(f"  开放性 (Openness): {person.personality.openness:.2f}")
    print(f"  尽责性 (Conscientiousness): {person.personality.conscientiousness:.2f}")
    print(f"  外向性 (Extraversion): {person.personality.extraversion:.2f}")
    print(f"  宜人性 (Agreeableness): {person.personality.agreeableness:.2f}")
    print(f"  神经质 (Neuroticism): {person.personality.neuroticism:.2f}")
    print(f"  AI 生成的特征标签 (Traits): {', '.join(person.personality.traits)}")
    print("----------------------------------------------------")

if __name__ == "__main__":
    asyncio.run(main())