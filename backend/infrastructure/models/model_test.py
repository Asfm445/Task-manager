from datetime import date, datetime, time

from infrastructure.db.session import Base
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from .model import DayPlan, StopProgress, Task, TaskProgress, TimeLog, User

# --- Setup an in-memory SQLite DB for testing ---
engine = create_engine("sqlite:///:memory:", echo=True)  # echo=True shows SQL executed
SessionLocal = sessionmaker(bind=engine)
Base.metadata.create_all(engine)


def print_counts(session):
    print(
        {
            "Users": session.query(User).count(),
            "Tasks": session.query(Task).count(),
            "DayPlans": session.query(DayPlan).count(),
            "TimeLogs": session.query(TimeLog).count(),
            "TaskProgress": session.query(TaskProgress).count(),
            "StopProgress": session.query(StopProgress).count(),
        }
    )


def run_test():
    session = SessionLocal()

    # 1️⃣ Create a user with:
    #    - one task (with subtask)
    #    - one dayplan (with timelog)
    user = User(username="alice", email="alice@example.com", hashed_password="123")
    session.add(user)
    session.commit()

    main_task = Task(description="Main task", owner=user)
    sub_task = Task(description="Sub task", main_task=main_task, owner=user)
    progress = TaskProgress(
        task=main_task,
        start_date=datetime.now(),
        end_date=datetime.now(),
        status="pending",
        estimated_hr=2,
    )
    stop_prog = StopProgress(task=main_task, stopped_at=datetime.now())

    dayplan = DayPlan(date=date.today(), user=user)
    timelog = TimeLog(
        task=main_task, plan=dayplan, start_time=time(9, 0), end_time=time(10, 0)
    )

    session.add_all([main_task, sub_task, progress, stop_prog, dayplan, timelog])
    session.commit()

    print("\nInitial counts:")
    print_counts(session)

    # 2️⃣ Delete main task — should delete subtask, progress, stop_progress, timelog
    session.delete(main_task)
    session.commit()

    print(
        "\nAfter deleting main task (subtask, progress, stop_progress, timelog should be gone but user/dayplan should remain):"
    )
    print_counts(session)

    # 3️⃣ Delete dayplan — should delete its timelogs (if any left)
    session.delete(dayplan)
    session.commit()

    print("\nAfter deleting dayplan (timelogs should be gone):")
    print_counts(session)

    # 4️⃣ Delete user — should delete everything linked
    session.delete(user)
    session.commit()

    print("\nAfter deleting user (everything should be gone):")
    print_counts(session)

    session.close()


if __name__ == "__main__":
    run_test()
    run_test()
    run_test()
