import asyncio
import os

from dotenv import load_dotenv
from sqlalchemy.exc import OperationalError
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import declarative_base, sessionmaker

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

engine = create_async_engine(DATABASE_URL, echo=True)

AsyncSessionLocal = sessionmaker(
    bind=engine,
    autocommit=False,
    autoflush=False,
    class_=AsyncSession
)

Base = declarative_base()

# Dependency
# async def get_db():
#     async with AsyncSessionLocal() as session:
#         yield session

async def get_db():
    max_retries = 5  # number of times to retry
    delay_seconds =3  # wait time between retries

    for attempt in range(max_retries):
        try:
            async with AsyncSessionLocal() as session:
                # test the connection
                await session.execute("SELECT 1")
                yield session
            break
        except OperationalError:
            if attempt < max_retries - 1:
                print(f"DB not ready, retrying in {delay_seconds}s... (attempt {attempt+1})")
                await asyncio.sleep(delay_seconds)
            else:
                print("Could not connect to DB after multiple attempts!")
                raise