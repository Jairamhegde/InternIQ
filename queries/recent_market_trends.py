import sqlite3
from dbconnection.dbconnect import connect_database
from utils.path import JOBS_DB
import pandas as pd



def Top_role():
        with connect_database(JOBS_DB) as conn:
                query = '''
                        SELECT J_title,count(*) as job_count ,postedDate
                        FROM jobs 
                        WHERE postedDate >= date('now','-10 days')
                        GROUP BY J_title
                        ORDER BY job_count DESC
                        limit 5;
                        '''
                df =pd.read_sql_query(query,conn)
                return df
def top_skill():
         with connect_database(JOBS_DB) as conn:
                query = '''
                        SELECT s.name as skill, count(*) as skill_count
                        FROM jobs j
                        join job_skills js on j.J_id=js.job_id
                        join skills s on js.skill_id = s.s_id
                        WHERE j.postedDate >= date("now","-10 days")
                        GROUP BY s.name
                        ORDER BY skill_count DESC
                        limit 5;
                        '''
                df = pd.read_sql_query(query,conn)
                return df

def total_opportunities():
         with connect_database(JOBS_DB) as conn:
                query = '''
                        SELECT count(*) as total_opportunities
                        FROM jobs
                        where postedDate >= date("now","-10 days");
                        '''
                df = pd.read_sql_query(query,conn)
                return df
