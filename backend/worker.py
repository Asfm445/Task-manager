import asyncio
import os
import logging
from datetime import datetime, timezone
from sqlalchemy import select
from dotenv import load_dotenv

from infrastructure.db.session import AsyncSessionLocal
from infrastructure.models.model import Task
from infrastructure.repositories.dayplan_repository import DayPlanRepository
from infrastructure.repositories.task_repository import TaskRepository
from infrastructure.services.ai_service import AIServiceImpl
from domain.models.dayplan_model import TaskAndTimeLogs

load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("worker")

async def run_analysis(task_id: int, ai_service: AIServiceImpl, db_session):
    task_repo = TaskRepository(db_session)
    dayplan_repo = DayPlanRepository(db_session)
    
    # Get task ORM object directly
    result = await db_session.execute(select(Task).filter(Task.id == task_id))
    orm_task = result.scalar_one_or_none()
    
    if not orm_task:
        logger.error(f"Task {task_id} not found")
        return

    logger.info(f"Analyzing task {task_id}: {orm_task.description}")

    # Calculate stats (similar to TaskService)
    now = datetime.now(timezone.utc)
    if orm_task.estimated_hr > 0:
        curr_completion_rate = orm_task.done_hr / orm_task.estimated_hr
    else:
        curr_completion_rate = 0

    # Get logs
    time_logs = await dayplan_repo.get_time_logs_by_task_id_and_minimum_date(orm_task.id, orm_task.start_date)
    
    if not time_logs:
        logger.info(f"No time logs for task {task_id}, skipping AI.")
        # Mark as analyzed with empty results to avoid re-polling
        orm_task.ai_feedback = "No activity logs yet for this task."
        orm_task.ai_recommendations = "Keep working on your task to get recommendations!"
        await db_session.commit()
        return

    task_time_log = TaskAndTimeLogs(
        task_description=orm_task.description,
        time_logs=time_logs,
        task_start_date=orm_task.start_date.date() if orm_task.start_date else datetime.now().date(),
        task_end_date=orm_task.end_date.date() if orm_task.end_date else datetime.now().date(),
        task_done_hr=orm_task.done_hr,
        task_completion_rate=curr_completion_rate * 100, # Converting to percentage as expected by prompt
        task_estimated_hr=orm_task.estimated_hr,
    )

    try:
        ai_result = await ai_service.analyze_and_recommend(task_time_log)
        
        # Update DB
        orm_task.ai_feedback = ai_result.feedback
        orm_task.ai_recommendations = ai_result.recommendations
        
        await db_session.commit()
        logger.info(f"Successfully analyzed task {task_id}")
    except Exception as e:
        logger.error(f"Error calling AI for task {task_id}: {str(e)}")
        await db_session.rollback()

async def worker_loop():
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        logger.error("GEMINI_API_KEY not found in environment!")
        return

    ai_service = AIServiceImpl(api_key)
    logger.info("AI Worker started, polling for tasks...")

    while True:
        try:
            async with AsyncSessionLocal() as db:
                # Find tasks that need analysis (ai_feedback is NULL)
                result = await db.execute(select(Task.id).where(Task.ai_feedback == None))
                task_ids = result.scalars().all()
                
                if not task_ids:
                    # logger.info("No tasks to analyze. Sleeping...")
                    await asyncio.sleep(10)
                    continue

                for t_id in task_ids:
                    await run_analysis(t_id, ai_service, db)
                    
        except Exception as e:
            logger.error(f"Worker loop error: {str(e)}")
            await asyncio.sleep(10)

if __name__ == "__main__":
    asyncio.run(worker_loop())
