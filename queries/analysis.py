import sqlite3
import pandas as pd
from pathlib import Path
from utils.path import JOBS_DB


# Helper to get a DB connection with helpful error when the file is missing
def get_conn():
    db_path = Path(JOBS_DB)
    if not db_path.exists():
        raise FileNotFoundError(
            f"Database file not found at {db_path}. Ensure jobs.db is present in the repository and deployed."
        )
    return sqlite3.connect(str(db_path))
# ------------------------------FOR OVERALL MARKET TRENDS----
def topSkills():
    # db_path = 'jobs.db'
    conn = get_conn()
    query = '''
    SELECT s.name, count(*) as demand
    FROM skills s
    JOIN job_skills js ON s.s_id = js.skill_id
    GROUP BY s.name
    ORDER BY demand DESC
    limit 10;
    '''
    df = pd.read_sql_query(query, conn)
    conn.close()
    return df
def roles():
    # db_path = 'jobs.db'
    conn = get_conn()
    query='''
    SELECT j.J_title,count(j.J_title) as demand
    FROM jobs j
    GROUP BY J_title
    ORDER BY demand DESC
    LIMIT 10;
    '''
    df=pd.read_sql_query(query,conn)
    conn.close()
    return df
def noOfopportunities():
    conn = get_conn()
    query = '''
    SELECT count(*) as opportunities
    FROM jobs ;
    '''
    df=pd.read_sql_query(query,conn)
    conn.close()
    return df['opportunities'][0]
def topLocations():
    # db_path = 'jobs.db'
    conn = get_conn()
    query='''
    SELECT j.location ,count(j.location) as count
    FROM jobs j
    GROUP BY j.location
    ORDER BY count DESC
    limit 10;
'''
    df=pd.read_sql_query(query,conn)
    conn.close()
    return df
def commonSkills():
    # db_path = 'jobs.db'
    conn = get_conn()
    query='''
        SELECT
        s.name AS skill,
        COUNT(DISTINCT j.J_title) AS role_count,
        COUNT(*) AS total_occurrences
    FROM jobs j
    JOIN job_skills js ON j.j_id = js.job_id
    JOIN skills s ON s.s_id = js.skill_id
    WHERE j.J_title IN (
        SELECT J_title
        FROM jobs
        GROUP BY J_title
        ORDER BY COUNT(*) DESC
        LIMIT 2
    )
    GROUP BY s.name
    HAVING COUNT(DISTINCT j.J_title) = 2
ORDER BY total_occurrences DESC;

'''
    df=pd.read_sql_query(query,conn)
    conn.close()
    return df
# ---------------------Role specific analysis---------
def TopSkillsOfRole(role):
    # db_path = 'jobs.db'
    conn = get_conn()
    query='''
    SELECT s.name,count(*) as demand
    FROM skills s
    JOIN job_skills js ON s.s_id = js.skill_id
    JOIN jobs j ON js.job_id = j.j_id  
    WHERE j.J_title = ?
    GROUP BY s.name
    ORDER BY count(*) DESC
    LIMIT 10;
    '''
    df=pd.read_sql_query(query,conn,params=(role,))
    conn.close()
    return df
def jobCount(job):
    # db_path = 'jobs.db'
    conn = get_conn()
    query='''
    SELECT count(J_title) as no_of_jobs
    FROM jobs
    WHERE J_title=?;
'''
    df=pd.read_sql_query(query,conn,params=(job,))
    conn.close()
    return df
# ----------------------------------------------------

def last_scraped_time():
    # db_path = 'jobs.db'
    conn = get_conn()

    query='''
    SELECT max(scraped_time)
    from jobs;'''
    df=pd.read_sql_query(query,conn)
    conn.close()
    return df.iloc[0,0]
def roles_trends():
    top_roles='''
        with TopSkills as (
        SELECT ss.name 
        from jobs j
        join job_skills js on j.j_id = js.job_id
        join skills ss on js.skill_id = ss.s_id
        group by ss.name
        order  by count(*) desc
        limit 4 
        ),
        Ranked as (
        select strftime("%d",jsn.scraped_date) as month,s.name,count(*) as jobCount,
        rank() over(
        partition by strftime("%d",jsn.scraped_date)
        order by count(*) desc
        ) as rank
        from jobSnapshot jsn
        join jobs j on jsn.job_id = j.j_id
        join job_skills js on j.j_id = js.job_id
        join skills s on js.skill_id = s.s_id
        where s.name in (select name from TopSkills)
        group by month,s.name
        order by jobCount desc

        )
        select * from Ranked
        order by month,rank;
        '''
    conn = get_conn()
    df=pd.read_sql_query(top_roles,conn)
    conn.close()
    return df

#--------------------------FOR LAST 7 DAYS ANALYSIS -------------
def OPPORTUNITIES():
    conn=sqlite3.connect(JOBS_DB)
    query = '''
    SELECT count(*) as opportunities
    FROM jobs 
    where date(postedDate) >= date("now","-10 days");
    '''
    df=pd.read_sql_query(query,conn)
    conn.close()
    

    return df['opportunities'][0]


# --------------------Role Specifi Analysis----------------
def uniqueSkills(role):
    conn = sqlite3.connect(JOBS_DB)
    query = '''
        select count(distinct s.name) as skills
        from jobs j
        join job_skills js on j.j_id = js.job_id
        join skills s on js.skill_id = s.s_id
        where J_title = ?
    '''
    df = pd.read_sql_query(query,conn,params=(role,))
    conn.close()
    return df

def uniqueSkillCount(role):
     conn = sqlite3.connect(JOBS_DB)
     query = '''
        select s.name as skill,count(*) as count
        from jobs j
        join job_skills js on j.j_id = js.job_id
        join skills s on js.skill_id = s.s_id
        where j.J_title = ?
        group by s.name
        order by count(*) desc
        limit 8;
        '''
     df = pd.read_sql_query(query,conn, params=(role,))
     conn.close()
     return df
print(roles_trends())