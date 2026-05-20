import sqlite3
import pandas as pd
import os
from utils.path import RAWDATA_DB
conn = sqlite3.connect(RAWDATA_DB)
cur = conn.cursor()
# cur.execute("""
# CREATE TABLE JobData(
#             id integer primary key autoincrement,
#             title VARCHAR(50),
#             Salary VARCHAR(50),
#             location VARCHAR(50),
#             ScrapeTime DATE,
#             posted_date DATE
#             )

# """)
# cur.execute('''
# CREATE TABLE Skills(
            
#             skill_id integer primary key autoincrement,
#             name VARCHAR(20));
# ''')
# cur.execute('''
# CREATE TABLE JobSkills(
#             job_id integer,
#             skill_id integer,
#             FOREIGN KEY(job_id) references JobData(id),
#             FOREIGN KEY(skill_id) REFERENCES Skills(skill_id))
# ''')

('''
CREATE UNIQUE INDEX IF NOT EXISTS unique_job
            on JobData(title,location,company,posted_date);
''')

('''
create unique index if not exists unique_skill on Skills(name)
''')
cur.execute('''
create unique index if not exists unique_skills_jobs on JobSkills(job_id,skill_id)
''')
conn.commit()
conn.close()