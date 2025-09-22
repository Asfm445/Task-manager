import asyncio
import logging
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

# Create a logger
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

MAX_RETRIES = 5  # number of times to retry
INITIAL_DELAY = 3  # wait time between retries

async def get_db():
    max_retries = MAX_RETRIES  
    delay_seconds = INITIAL_DELAY  

    for attempt in range(max_retries):
        try:
            async with AsyncSessionLocal() as session:
                # test the connection
                await session.execute("SELECT 1")
                return session
        except OperationalError:
            if attempt < max_retries - 1:
                logger.warning(f"DB not ready, retrying in {delay_seconds}s... (attempt {attempt+1})")
                await asyncio.sleep(delay_seconds)
                delay_seconds = min(delay_seconds * 2, MAX_RETRIES * INITIAL_DELAY)
            else:
                logger.error("Could not connect to DB after multiple attempts!")
                raise OperationalError("Could not connect to database")
