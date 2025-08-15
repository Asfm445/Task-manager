import os
from logging.config import fileConfig
from sqlalchemy import create_engine
from alembic import context
from dotenv import load_dotenv

# Load env vars
load_dotenv()

# Alembic Config
config = context.config
fileConfig(config.config_file_name)

# Import models so Alembic knows metadata
from infrastructure.models.model import Base

target_metadata = Base.metadata

# Use sync DB URL for Alembic
DATABASE_URL_SYNC = os.getenv("DATABASE_URL_SYNC")

def run_migrations_offline():
    """Run migrations in 'offline' mode."""
    context.configure(
        url=DATABASE_URL_SYNC,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )
    with context.begin_transaction():
        context.run_migrations()

def run_migrations_online():
    """Run migrations in 'online' mode."""
    connectable = create_engine(DATABASE_URL_SYNC)
    with connectable.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata)
        with context.begin_transaction():
            context.run_migrations()

if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
