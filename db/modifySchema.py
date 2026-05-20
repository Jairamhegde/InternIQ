import sqlite3
import logging
import os
from utils.path import RAWDATA_DB
from utils.path import JOBS_DB
# logging.info("ade")
# cur.execute(
#     'ALTER TABLE jobs add company text'
# )
# cur.execute(
#     'CREATE UNIQUE INDEX IF NOT EXISTS idx_job_unique ON jobs (j_title, company, location)'
# )
# logging.info("Aded unique contrain on jobs")
# cur.execute(

#     "ALTER TABLE jobs RENAME COLUMN acraped_time TO scraped_time"
# )

# cur.execute(
#     "alter table skills rename to old_skil"
# )
# logging.info("Added scraped_time column to jobs table")
# cur.execute(
#     '''
#     CREATE TABLE jobsnd_skills(
#     job_id INT,
#     skill_id TEXT,
#     PRIMARY KEY(job_id,skill_id),
#     FOREIGN KEY(job_id)REFERENCES jobs(j_id) ON DELETE CASCADE,
#     FOREIGN KEY(skill_id)REFERENCES skills(s_id) ON DELETE CASCADE
#     )
# ;'''
# )
# cur.execute(
#     '''INSERT OR IGNORE INTO  jobsnd_skills(job_id,skill_id) SELECT job_id,skill_id from job_skills;
# '''
# )
# cur.execute(''' drop table jobsnd_skills''')
# cur.execute('''
# PRAGMA foreign_keys = on;
# ''')
# cur.execute('''
# ALTER TABLE jobsnd_skills rename to job_skills;
# ''')

# def clearTable():
#     conn=sqlite3.connect(db_path)
#     cur=conn.cursor()
#     cur.execute('DELETE FROM jobs')
#     cur.execute('DELETE FROM skills')
#     cur.execute('DELETE FROM job_skills')
#     cur.execute('DELETE FROM jobSnapshot')
#     conn.commit()
#     conn.close()
#     logging.info("cleared table...")

conn = sqlite3.connect(JOBS_DB)
# cur = conn.cursor()
# ('''
# create table jobSnapshot(
#             id integer primary key autoincrement,
#             title varchar(50),
#             company varchar(50),
#             location varchar(50)
#             );
# ''')

# cur.execute('ALTER TABLE jobSnapshot add scraped_date date;')
cur = conn.cursor()

cur.execute(''' create unique index if not exists uniquejob on jobs(J_title,location,company,postedDate)''')
conn.commit()
conn.close()
# cur.execute('''
# CREATE TABLE jobSnapshot(
#         job_id INT,
#         scraped_date date,
#         PRIMARY KEY(job_id,scraped_date));
# ''')

# cur.execute('''
# insert into jobSnapshot(job_id,scraped_date)
#             select j_id,scraped_time from jobs;




# query = """ALTER TABLE jobs
# MODIFY salary INT """

# minsalCol = '''
# ALTER TABLE jobs
# ADD minsal int;
# '''
# maxslaCol = '''
# ALTER TABLE jobs
# ADD maxsal int;
# '''

# fetchIdsal = '''
# SELECT j_id,salary FROM jobs;
# '''
# # cur.execute(query)
# # cur.execute(minsalCol)
# # cur.execute(maxslaCol)
# import pandas as pd
# query ="""select * from Jobs;"""

# df = pd.read_sql_query(query,conn)
# print(df)

# # cur.execute(fetchIdsal)

# rows = cur.fetchall()
# for row in rows:
    
#     rowid = row[0]
#     sal = row[1]
#     minsal = None
#     maxsal = None
#     if sal:
#         try:
    
#             if "-" in sal:
#                 minsal,maxsal = sal.split("-")
#                 minsal = int(minsal.replace(",","").replace("₹","").strip())
#                 maxsal = int(maxsal.replace(",","").replace("₹","").strip())
#             else:
#                 minsal = maxsal = int(sal.replace(",","").replace("₹","").strip())
#         except ValueError:
#             minsal = None
#             maxsal = None    
#     myquery = """
#     UPDATE jobs
#     SET minsal = ?,maxsal = ?
#     WHERE j_id = ?
#     """
#     # cur.execute(myquery,(minsal,maxsal,rowid))
    

# # Drop the salary column from jobs
# dropsal = """
# ALTER TABLE jobs
# drop Salary;
# """
# # cur.execute(dropsal)
# conn.commit()
# conn.close()
