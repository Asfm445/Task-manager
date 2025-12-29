import os
import time
import logging
from logging.handlers import RotatingFileHandler
from dotenv import load_dotenv
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware

# Import your routers
from api.routers import dayplan_router, task, user_router

load_dotenv()

app = FastAPI()

# --- PERFORMANCE LOGGING SETUP ---
# 1. Define the log format
log_formatter = logging.Formatter('%(asctime)s | %(levelname)s | %(message)s')

# 2. Setup the File Handler (Logs to 'api_performance.log', max 5MB, keeps 3 backups)
log_file = "api_performance.log"
file_handler = RotatingFileHandler(log_file, maxBytes=5*1024*1024, backupCount=3)
file_handler.setFormatter(log_formatter)

# 3. Configure the logger
perf_logger = logging.getLogger("performance")
perf_logger.setLevel(logging.INFO)
perf_logger.addHandler(file_handler)
# Also add to console so you see it in the terminal
perf_logger.addHandler(logging.StreamHandler()) 

@app.middleware("http")
async def log_performance(request: Request, call_next):
    start_time = time.perf_counter()
    
    response = await call_next(request)
    
    duration = time.perf_counter() - start_time
    
    # Format the log message for readability
    log_message = (
        f"Method: {request.method:<7} | "
        f"Path: {request.url.path:<25} | "
        f"Status: {response.status_code} | "
        f"Duration: {duration:.4f}s"
    )
    
    perf_logger.info(log_message)
    
    # Add to headers for client-side inspection
    response.headers["X-Response-Time"] = f"{duration:.4f}s"
    
    return response

# --- MIDDLEWARE & ROUTERS ---

app.add_middleware(
    CORSMiddleware,
    allow_origins=[os.getenv("FRONTEND_URL"), "http://192.168.210.194:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(task.router, prefix="/tasks", tags=["Tasks"])
app.include_router(dayplan_router.router, prefix="/plans", tags=["Plans"])
app.include_router(user_router.router, prefix="/auth", tags=["Authentication"])