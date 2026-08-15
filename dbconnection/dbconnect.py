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

def connect_database(search_path="clean_data"):
    if os.environ.get("HOST_NAME"):
        try:
            url = _build_url(
                user=os.environ["USER"],
                password=os.environ["PASSWORD"],
                host=os.environ["HOST_NAME"],
                port=os.environ["PORT"],
                database=os.environ["DATABASE"],
                sslmode=os.environ["SSLMODE"],
            )
            engine = create_engine(
                url,
                connect_args={"options": f"-c search_path={search_path}"}
            )
            return engine
        except Exception as e:
            logging.error(f"Error occurred in db_connection: {e}")
            raise  # or `return None` if you truly want silent failure — but handle it upstream
    else:
        return _connect_to_st(search_path)


def _connect_to_st(search_path):
    import streamlit as st

    @st.cache_resource
    def _cache(search_path):
        data = st.secrets["database"]
        url = _build_url(
            user=data["user"],
            password=data["password"],
            host=data["host"],
            port=data["port"],
            database=data["database"],
            sslmode=data["sslmode"],
        )
        return create_engine(
            url,
            connect_args={"options": f"-c search_path={search_path}"}
        )

    return _cache(search_path)