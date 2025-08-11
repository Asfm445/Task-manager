from infrastructure.db.session import Base
from sqlalchemy import (
    Boolean,
    Column,
    Date,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
    Table,
    Time,
)
from sqlalchemy.orm import relationship


class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)

    assigned_tasks = relationship(
        "Task", secondary="task_assignees", back_populates="assignees"
    )
    my_tasks = relationship(
        "Task",
        back_populates="owner",
        cascade="all, delete-orphan",  # If user deleted, delete their owned tasks
    )
    tokens = relationship(
        "Token",
        back_populates="user",
        cascade="all, delete-orphan",  # Delete tokens if user is deleted
    )
    day_plans = relationship(
        "DayPlan", back_populates="user", cascade="all, delete-orphan"
    )


class Task(Base):
    __tablename__ = "tasks"
    id = Column(Integer, primary_key=True, index=True)
    description = Column(String, index=True)
    end_date = Column(DateTime)
    estimated_hr = Column(Float)
    done_hr = Column(Float, default=0.0)
    is_repititive = Column(Boolean, default=False)
    status = Column(String, default="pending")
    start_date = Column(DateTime)
    main_task_id = Column(
        Integer, ForeignKey("tasks.id", ondelete="CASCADE"), nullable=True
    )
    owner_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"))
    is_stopped = Column(Boolean, default=False, nullable=False)

    # Cascade delete subtasks if main task is deleted
    main_task = relationship("Task", remote_side=[id], back_populates="subtasks")
    subtasks = relationship(
        "Task", back_populates="main_task", cascade="all, delete-orphan"
    )

    # Cascade delete related timelogs, progress, stop_progress
    time_logs = relationship(
        "TimeLog", back_populates="task", cascade="all, delete-orphan"
    )
    progress = relationship(
        "TaskProgress", back_populates="task", cascade="all, delete-orphan"
    )
    stop_progress = relationship(
        "StopProgress", back_populates="task", cascade="all, delete-orphan"
    )

    assignees = relationship(
        "User", secondary="task_assignees", back_populates="assigned_tasks"
    )
    owner = relationship("User", foreign_keys=[owner_id], back_populates="my_tasks")


task_assignees = Table(
    "task_assignees",
    Base.metadata,
    Column("user_id", Integer, ForeignKey("users.id", ondelete="CASCADE")),
    Column("task_id", Integer, ForeignKey("tasks.id", ondelete="CASCADE")),
)


class DayPlan(Base):
    __tablename__ = "plans"

    id = Column(Integer, primary_key=True, index=True)
    date = Column(Date, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"))
    user = relationship("User", back_populates="day_plans")

    # Cascade delete timelogs if dayplan deleted
    times = relationship("TimeLog", back_populates="plan", cascade="all, delete-orphan")


class TimeLog(Base):
    __tablename__ = "times"

    id = Column(Integer, primary_key=True, index=True)
    end_time = Column(Time)
    start_time = Column(Time)
    task_id = Column(Integer, ForeignKey("tasks.id", ondelete="CASCADE"))
    plan_id = Column(Integer, ForeignKey("plans.id", ondelete="CASCADE"))

    plan = relationship("DayPlan", back_populates="times")
    task = relationship("Task", back_populates="time_logs")


class TaskProgress(Base):
    __tablename__ = "task_progress"

    id = Column(Integer, primary_key=True, index=True)
    task_id = Column(Integer, ForeignKey("tasks.id", ondelete="CASCADE"))
    start_date = Column(DateTime)
    end_date = Column(DateTime)
    status = Column(String)
    done_hr = Column(Float, default=0.0)
    estimated_hr = Column(Float)

    task = relationship("Task", back_populates="progress")


class StopProgress(Base):
    __tablename__ = "stop_progress"

    id = Column(Integer, primary_key=True, index=True)
    stopped_at = Column(DateTime)
    task_id = Column(Integer, ForeignKey("tasks.id", ondelete="CASCADE"))

    task = relationship("Task", back_populates="stop_progress")


class Token(Base):
    __tablename__ = "tokens"

    id = Column(String, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"))
    token = Column(String)
    expired_at = Column(DateTime)
    created_at = Column(DateTime)

    user = relationship("User", back_populates="tokens")
