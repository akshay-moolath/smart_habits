from logging.config import fileConfig

from sqlalchemy import engine_from_config
from sqlmodel import SQLModel
from sqlalchemy import pool

from alembic import context
import os
from dotenv import load_dotenv

# --- BEGIN: CRITICAL FIX FOR MODEL DISCOVERY ---
import sys
from os.path import abspath, dirname

# This line adds your project's root directory to the Python path.
# It allows 'env.py' to successfully import modules defined in 'app/'.
sys.path.append(dirname(dirname(abspath(__file__))))

# Import all modules that contain your SQLModel classes.
# This registers your tables with SQLModel.metadata.
# NOTE: Ensure 'app.models' is the correct location for your User model.
from app.models import User 
# If you have other models, import them here as well (e.g., from app.models import Habit)
# --- END: CRITICAL FIX ---

load_dotenv()

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# 1. Retrieve the DATABASE_URL from the environment
db_url = os.environ.get("DATABASE_URL")

# 2. Set the URL onto the Alembic config object globally
if db_url:
    config.set_main_option("sqlalchemy.url", db_url)
else:
    # This check ensures we fail fast if the environment variable is missing
    raise ValueError("DATABASE_URL environment variable is not set in .env or shell.")


# Interpret the config file for Python logging.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# add your model's MetaData object here for 'autogenerate' support
# target_metadata is now correctly aware of your models due to the imports above
target_metadata = SQLModel.metadata


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode."""
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode.
    
    Creates an Engine and associates a connection with the context.
    """
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection, target_metadata=target_metadata
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()