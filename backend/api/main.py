from api.routers import dayplan_router, task, user_router
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from infrastructure.db.session import engine
from infrastructure.models import model

app = FastAPI()

# Allow your frontend's origin
origins = [
    "http://localhost:5173",  # React dev server
    # Add more origins if needed
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,  # Allowed origins
    allow_credentials=True,
    allow_methods=["*"],  # Allow all HTTP methods (GET, POST, etc.)
    allow_headers=["*"],  # Allow all headers
)



model.Base.metadata.create_all(bind=engine)


app.include_router(task.router, prefix="/tasks", tags=["Tasks"])
app.include_router(dayplan_router.router, prefix="/plans", tags=["Plans"])
# app.include_router(times.router, prefix="/times", tags=["Times"])
app.include_router(user_router.router, prefix="/auth", tags=["Authentication"])
