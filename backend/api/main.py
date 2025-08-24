import os

from api.routers import dayplan_router, task, user_router
from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

load_dotenv()

app = FastAPI()


app.add_middleware(
    CORSMiddleware,
    allow_origins=[os.getenv("FRONTEND_URL")],  # Allowed origins
    allow_credentials=True,
    allow_methods=["*"],  # Allow all HTTP methods (GET, POST, etc.)
    allow_headers=["*"],  # Allow all headers
)



# model.Base.metadata.create_all(bind=engine)


app.include_router(task.router, prefix="/tasks", tags=["Tasks"])
app.include_router(dayplan_router.router, prefix="/plans", tags=["Plans"])
# app.include_router(times.router, prefix="/times", tags=["Times"])
app.include_router(user_router.router, prefix="/auth", tags=["Authentication"])
