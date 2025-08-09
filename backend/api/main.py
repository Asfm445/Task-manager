from api.routers import task, user_router
from fastapi import FastAPI

app = FastAPI()

app.include_router(task.router, prefix="/tasks", tags=["Tasks"])
# app.include_router(plan.router, prefix="/plans", tags=["Plans"])
# app.include_router(times.router, prefix="/times", tags=["Times"])
app.include_router(user_router.router, prefix="/auth", tags=["Authentication"])
