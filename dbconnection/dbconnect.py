import psycopg2
import os
import logging
from dotenv import load_dotenv


load_dotenv()
def connect_database(search_path="clean_data"):
    if os.environ.get("HOST_NAME"):
        PG_CONFIG = {
            "host": os.environ['HOST_NAME'],
            "database": os.environ['DATABASE'],
            "user": os.environ['USER'],
            "password": os.environ['PASSWORD'],
            "port": os.environ['PORT'],
            "sslmode": os.environ['SSLMODE']
        }
        try:
            conn = psycopg2.connect(**PG_CONFIG)
            cur = conn.cursor()
            cur.execute("SET search_path TO %s",(search_path,))
            cur.close()
            return conn
        except Exception as e:
            logging.error(f"Error occured in db_connection :{e}")
    else:
        return  _connect_to_st(search_path)
         

def _connect_to_st(search_path):
        import streamlit as st

        @st.cache_resource
        def _cache(search_path):
            data = st.secrets["database"]
            PG_CONFIG = {
                "host": data['host'],
                "database": data['database'],
                "user": data['user'],
                "password": data['password'],
                "port": data['port'],
                "sslmode" : data['sslmode']
            }
            try:
                conn = psycopg2.connect(**PG_CONFIG)
                cur = conn.cursor()
                cur.execute("SET search_path TO %s", (search_path,))
                cur.close()
                return conn
            except psycopg2.OperationalError as e:
                raise ConnectionError(
                    f"Could not connect to PostgreSQL database '{PG_CONFIG['database']}' "
                    f"at {PG_CONFIG['host']}:{PG_CONFIG['port']}. Check your config and ensure the server is running.\n{e}"
                )
        return _cache(search_path)

