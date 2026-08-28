import os
import logging
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.engine import URL

load_dotenv()

def _build_url(user, password, host, port, database, sslmode):
    return URL.create(
        drivername="postgresql+psycopg2",
        username=user,
        password=password,
        host=host,
        port=port,
        database=database,
        query={"sslmode": sslmode},
    )

_engines = {}

def connect_database(search_path="clean_data"):
    global _engines
    if os.environ.get("DB_HOST"):
        if search_path not in _engines:
            try:
                url = _build_url(
                    user=os.environ["DB_USER"],
                    password=os.environ["DB_PASSWORD"],
                    host=os.environ["DB_HOST"],
                    port=os.environ["DB_PORT"],
                    database=os.environ["DB_NAME"],
                    sslmode=os.environ.get("SSLMODE", "require"),
                )
                _engines[search_path] = create_engine(
                    url,
                    connect_args={"options": f"-c search_path={search_path}"},
                    pool_size=5,
                    max_overflow=10
                )
            except Exception as e:
                logging.error(f"Error occurred in db_connection: {e}")
                raise
        return _engines[search_path]
    else:
        raise ValueError("DB_HOST environment variable is missing. Please ensure your .env file is loaded.")