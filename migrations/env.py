from logging.config import fileConfig

from alembic import context
from sqlalchemy import create_engine, pool

from dbconnection.dbconnect import get_database_url

config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# The tables were created by hand, not from SQLAlchemy models, so there is no
# metadata to autogenerate from. Every migration is written by hand.
target_metadata = None

# The tables live in the raw_data and clean_data schemas, so each migration names
# its schema explicitly. Alembic's own version table is kept in public.
VERSION_TABLE_SCHEMA = "public"


def run_migrations_offline() -> None:
    """`alembic upgrade head --sql`: prints the SQL instead of running it."""
    context.configure(
        url="postgresql://",
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        version_table_schema=VERSION_TABLE_SCHEMA,
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    engine = create_engine(get_database_url(), poolclass=pool.NullPool)

    with engine.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            version_table_schema=VERSION_TABLE_SCHEMA,
        )
        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
