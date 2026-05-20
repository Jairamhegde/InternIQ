import sqlite3
def connect_database(dbname):
    return sqlite3.connect(dbname)
