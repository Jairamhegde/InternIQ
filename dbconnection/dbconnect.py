import psycopg2
import streamlit as st


@st.cache_resource
def connect_database(search_path="clean_data"):
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
    
