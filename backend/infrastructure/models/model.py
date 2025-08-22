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
from sqlalchemy.sql import func


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    verified=Column(Boolean, default=False)
    role=Column(String, default="user")

    assigned_tasks = relationship(
        "Task",
        secondary="task_assignees",
        back_populates="assignees",
        lazy="selectin",
    )
    my_tasks = relationship(
        "Task",
        back_populates="owner",
        cascade="all, delete-orphan",
        lazy="selectin",
    )
    tokens = relationship(
        "Token",
        back_populates="user",
        cascade="all, delete-orphan",
        lazy="selectin",
    )
    day_plans = relationship(
        "DayPlan", back_populates="user", cascade="all, delete-orphan", lazy="selectin"
    )


class Task(Base):
    __tablename__ = "tasks"

    id = Column(Integer, primary_key=True, index=True)
    description = Column(String, index=True)
    start_date = Column(DateTime(timezone=True))
    end_date = Column(DateTime(timezone=True))
    estimated_hr = Column(Float)
    done_hr = Column(Float, default=0.0)
    is_repititive = Column(Boolean, default=False)
    status = Column(String, default="pending")
    owner_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"))
    main_task_id = Column(Integer, ForeignKey("tasks.id", ondelete="CASCADE"), nullable=True)
    is_stopped = Column(Boolean, default=False, nullable=False)

    main_task = relationship("Task", remote_side=[id], back_populates="subtasks", lazy="selectin")
    subtasks = relationship(
        "Task", back_populates="main_task", cascade="all, delete-orphan", lazy="selectin"
    )
    time_logs = relationship(
        "TimeLog", back_populates="task", cascade="all, delete-orphan", lazy="selectin"
    )
    progress = relationship(
        "TaskProgress", back_populates="task", cascade="all, delete-orphan", lazy="selectin"
    )
    stop_progress = relationship(
        "StopProgress", back_populates="task", cascade="all, delete-orphan", lazy="selectin"
    )
    assignees = relationship(
        "User", secondary="task_assignees", back_populates="assigned_tasks", lazy="selectin"
    )
    owner = relationship("User", foreign_keys=[owner_id], back_populates="my_tasks", lazy="selectin")


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
    user = relationship("User", back_populates="day_plans", lazy="selectin")

    times = relationship("TimeLog", back_populates="plan", cascade="all, delete-orphan", lazy="selectin")


class TimeLog(Base):
    __tablename__ = "times"

    id = Column(Integer, primary_key=True, index=True)
    start_time = Column(Time)
    end_time = Column(Time)
    task_id = Column(Integer, ForeignKey("tasks.id", ondelete="CASCADE"))
    plan_id = Column(Integer, ForeignKey("plans.id", ondelete="CASCADE"))
    done = Column(Boolean, default=False)

    plan = relationship("DayPlan", back_populates="times", lazy="selectin")
    task = relationship("Task", back_populates="time_logs", lazy="selectin")


class TaskProgress(Base):
    __tablename__ = "task_progress"

    id = Column(Integer, primary_key=True, index=True)
    task_id = Column(Integer, ForeignKey("tasks.id", ondelete="CASCADE"))
    start_date = Column(DateTime(timezone=True))
    end_date = Column(DateTime(timezone=True))
    status = Column(String)
    done_hr = Column(Float, default=0.0)
    estimated_hr = Column(Float)

    task = relationship("Task", back_populates="progress", lazy="selectin")


class StopProgress(Base):
    __tablename__ = "stop_progress"

    id = Column(Integer, primary_key=True, index=True)
    task_id = Column(Integer, ForeignKey("tasks.id", ondelete="CASCADE"))
    stopped_at = Column(DateTime(timezone=True))

    task = relationship("Task", back_populates="stop_progress", lazy="selectin")


class Token(Base):
    __tablename__ = "tokens"

    id = Column(String, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"))
    token = Column(String)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    expired_at = Column(DateTime(timezone=True))

    user = relationship("User", back_populates="tokens", lazy="selectin")
