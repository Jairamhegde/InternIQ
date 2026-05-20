import pandas as pd
import os
from extract.extractor import scrape_data
from utils.path import RAWDATA_DB
from utils.path import JOBS_DB
from utils.path import TEST_DB
import sqlite3
import re



conn = sqlite3.connect(JOBS_DB)

cur1 = conn.cursor()
fetch_all_cols = '''
SELECT * FROM skills;'''
cur1.execute(fetch_all_cols)
rows = cur1.fetchall()
cur1.execute('DELETE FROM skills;')


for row in rows:
    s_id = row[0]
    sname = " ".join(row[1].strip().split()).lower()
    cur1.execute('''
        insert or ignore into skills(s_id,name) values
                 (?,?)''',(s_id,sname))
conn.commit()
conn.close()
print("Done")


