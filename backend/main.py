from api.routers import plan, task, times
from auth import auth
from fastapi import FastAPI

app = FastAPI()

app.include_router(task.router, prefix="/tasks", tags=["Tasks"])
# app.include_router(plan.router, prefix="/plans", tags=["Plans"])
# app.include_router(times.router, prefix="/times", tags=["Times"])
app.include_router(auth.router, prefix="/auth", tags=["Authentication"])
