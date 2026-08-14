import os
import logging
from dotenv import load_dotenv
from sqlalchemy import create_engine, text


load_dotenv()

def connect_database(search_path="clean_data"):
    if os.environ.get("HOST_NAME"):
        url = (
            f"postgresql+psycopg2://{os.environ['USER']}:{os.environ['PASSWORD']}"
            f"@{os.environ['HOST_NAME']}:{os.environ['PORT']}/{os.environ['DATABASE']}"
            f"?sslmode={os.environ['SSLMODE']}"
        )
        try:
            engine = create_engine(
                url,
                connect_args={"options": f"-c search_path={search_path}"}
            )
            return engine
        except Exception as e:
            logging.error(f"Error occured in db_connection :{e}")
    else:
        return  _connect_to_st(search_path)
         

def _connect_to_st(search_path):
    import streamlit as st
    @st.cache_resource
    def _cache(search_path):
        data = st.secrets["database"]
        url = (
            f"postgresql+psycopg2://{data['user']}:{data['password']}"
            f"@{data['host']}:{data['port']}/{data['database']}"
            f"?sslmode={data['sslmode']}"
        )
        engine = create_engine(
            url,
            connect_args={"options": f"-c search_path={search_path}"}
        )
        return engine
    return _cache(search_path)