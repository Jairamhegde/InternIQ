
from sqlalchemy import true
import numpy as np

import pandas as pd
from dbconnection.dbconnect import connect_database
from datetime import datetime


# ------------------------------FOR OVERALL MARKET TRENDS----

def topSkills(field:str | None= None):
    conn = connect_database("clean_data")
    query = '''
    SELECT s.name, count(*) as demand
    FROM skills s
    JOIN job_skills js ON s.skill_id = js.skill_id'''

    params = []
    if field:
        query += \
        ''' JOIN job_data j on js.job_id = j.job_id
            where primary_field = %s
        '''
        params.append(field)

    query += \
    '''
    GROUP BY s.name
    ORDER BY demand DESC
    LIMIT 6;'''
    
    df = pd.read_sql_query(query, conn, params=(tuple(params) if params else None))

    return df


def roles():
    conn = connect_database("clean_data")
    query = '''
    SELECT job_id,title,count(*) as demand
    FROM job_data 
    GROUP BY job_id,title
    ORDER BY demand DESC
    LIMIT 10;
    '''
    df = pd.read_sql_query(query, conn)
    return df

def toproles(field:str | None = None):
    conn = connect_database("clean_data")
    query = '''
    select title as role,count(*) as volume
    from job_data
    '''
    params = []
    if field:
        query += " where primary_field = %s"
        params.append(field)
        
    query += '''
    group by title
    order by  volume desc
    LIMIT 6;
    '''
    df = pd.read_sql_query(query, conn, params=(tuple(params) if params else None))

    return df




def noOfopportunities(field:str | None = None):
    conn = connect_database()
    query = '''
    SELECT count(*) as opportunities
    FROM job_data
    '''
    parameter = []
    if field:
        query += " where primary_field = %s"
        parameter.append(field)
    df = pd.read_sql_query(query, conn, params=(tuple(parameter) if parameter else None))

    return df['opportunities'][0]


def topLocations(field:str | None = None):
    conn = connect_database("clean_data")
    query = '''
    SELECT j.location, count(j.location) as count
    FROM job_data j'''
    parameter = []
    if field:
        query += " where primary_field = %s"
        parameter.append(field)
    query += '''
    GROUP BY j.location
    ORDER BY count DESC
    LIMIT 10;
    '''
    df = pd.read_sql_query(query, conn, params=(tuple(parameter) if parameter else None))

    return df


def commonSkills():
    conn = connect_database("clean_data")
    query = '''
    SELECT
        s.name AS skill,
        COUNT(DISTINCT j.job_id) AS role_count,
        COUNT(*) AS total_occurrences
    FROM job_data j
    JOIN job_skills js ON j.job_id = js.job_id
    JOIN skills s ON s.skill_id = js.skill_id
    WHERE j.job_id IN (
        SELECT job_id
        FROM job_data
        GROUP BY job_id
        ORDER BY COUNT(*) DESC
        LIMIT 2
    )
    GROUP BY s.name
    HAVING COUNT(DISTINCT j.job_id) = 2
    ORDER BY total_occurrences DESC;
    '''
    df = pd.read_sql_query(query, conn)

    return df


# ---------------------Role specific analysis---------

def TopSkillsOfRole(role):
    conn = connect_database("clean_data")
    query = '''
    SELECT s.name, count(*) as demand
    FROM skills s
    JOIN job_skills js ON s.skill_id = js.skill_id
    JOIN job_data j ON js.job_id = j.job_id
    WHERE j.title = %s
    GROUP BY s.name
    ORDER BY count(*) DESC
    LIMIT 10;
    '''
    df = pd.read_sql_query(query, conn, params=(role,))

    return df


def jobCount(job):
    conn = connect_database("clean_data")
    query = '''
    SELECT count(*) as no_of_jobs
    FROM job_data
    WHERE title = %s;
    '''
    df = pd.read_sql_query(query, conn, params=(job,))

    return df


# ----------------------------------------------------ROLE TRENDS(TRENDS OVER TIME)-------------------

def last_scraped_time():
    conn = connect_database("clean_data")
    query = '''
    SELECT max(scrape_time)
    FROM job_data;
    '''
    df = pd.read_sql_query(query, conn)

    return df.iloc[0, 0]


def roles_trends(field:str | None = None):
    query = '''
    WITH TopSkills AS (
        SELECT ss.name
        FROM job_data j
        JOIN job_skills js ON j.job_id = js.job_id
        JOIN skills ss ON js.skill_id = ss.skill_id
    '''
    params = []
    if field:
        query += " WHERE j.primary_field = %s"
        params.append(field)
        
    query += '''
        GROUP BY ss.name
        ORDER BY count(*) DESC
        LIMIT 4
    ),
    Ranked AS (
        SELECT
            TO_CHAR(jsn.scraped_date, 'YYYY-MM-DD') AS month,
            s.name,
            count(*) AS jobCount,
            RANK() OVER (
                PARTITION BY TO_CHAR(jsn.scraped_date, 'YYYY-MM-DD')
                ORDER BY count(*) DESC
            ) AS rank
        FROM "job_snapshot" jsn
        JOIN job_data j ON jsn.job_id = j.job_id
        JOIN job_skills js ON j.job_id = js.job_id
        JOIN skills s ON js.skill_id = s.skill_id
        WHERE s.name IN (SELECT name FROM TopSkills)
    '''
    
    if field:
        query += " AND j.primary_field = %s"
        params.append(field)
        
    query += '''
        GROUP BY TO_CHAR(jsn.scraped_date, 'YYYY-MM-DD'), s.name
    )
    SELECT * FROM Ranked
    ORDER BY month, rank;
    '''
    conn = connect_database("clean_data")
    df = pd.read_sql_query(query, conn, params=(tuple(params) if params else None))

    return df

# --------------------------FOR LAST 7 DAYS ANALYSIS -------------

def OPPORTUNITIES():
    conn = connect_database("clean_data")
    query = '''
    SELECT count(*) as opportunities
    FROM job_data
    WHERE postedDate::date >= CURRENT_DATE - INTERVAL '10 days';
    '''
    df = pd.read_sql_query(query, conn)

    return df['opportunities'][0]


# --------------------Role Specific Analysis----------------

def uniqueSkills(role):
    conn = connect_database("clean_data")
    query = '''
    SELECT count(distinct s.name) as skills
    FROM job_data j
    JOIN job_skills js ON j.job_id = js.job_id
    JOIN skills s ON js.skill_id = s.skill_id
    WHERE j.job_id = %s
    '''
    df = pd.read_sql_query(query, conn, params=(role,))

    return df


def uniqueSkillCount(role):
    conn = connect_database("clean_data")
    query = '''
    SELECT s.name as skill, count(*) as count
    FROM job_data j
    JOIN job_skills js ON j.job_id = js.job_id
    JOIN skills s ON js.skill_id = s.skill_id
    WHERE j.job_id = %s
    GROUP BY s.name
    ORDER BY count(*) DESC
    LIMIT 8;
    '''
    df = pd.read_sql_query(query, conn, params=(role,))

    return df


#------------------------JOB-POSTINGS----------------------

def job_postings(year,field:str | None = None):
    conn = connect_database('clean_data')
    parameter =[]
    parameter.append(year)
    query = '''
    SELECT 
    TO_CHAR( posted_date::date,'month') AS month,
    COUNT(*) AS jobs
    FROM clean_data.job_data
    WHERE EXTRACT(year from posted_date::date) = %s'''

    if field:
        query += " and primary_field = %s"
        parameter.append(field)
    query += '''
    GROUP BY TO_CHAR( posted_date::date,'month')
    ORDER BY min(extract(month from posted_date::date)) asc;
    '''
    df = pd.read_sql_query(query,conn,params=tuple(parameter))
    return df

def current_year_postings(year ,field:str | None =None):
    conn = connect_database('clean_data')
    query = '''
    select count(*) as job_postings
    from job_data
    where extract(year from posted_date::date) = %s
    '''
    parameter = []
    parameter.append(year)
    if field:
        query += " and primary_field = %s"
        parameter.append(field)
    df = pd.read_sql_query(query,conn,params=tuple(parameter))
    return df.iloc[0]['job_postings']



# -----------------------COMPARITIVE ANALYSIS--------------------

def common_skills(job_roles):
    conn = connect_database('clean_data')

    n = len(job_roles)
    if n < 1:
        return []

    parameter = ", ".join(["%s"]*n)
    query =f'''
    SELECT s.name 
    FROM clean_data.job_data j
    JOIN clean_data.job_skills js ON j.job_id = js.job_id
    JOIN clean_data.skills s ON js.skill_id = s.skill_id
    WHERE j.title in ({parameter})
    GROUP BY s.name
    HAVING count(distinct j.title) = %s;
    '''
    place_hollder = (*job_roles,n)

    df = pd.read_sql_query(query,conn,params=place_hollder)
    return df

def get_percentage_ofskills(job_roles):

    n = len(job_roles)
    conn = connect_database('clean_data')


    parameter = ", ".join(["%s"]*n)
    query = f"""
        WITH common_skills AS (

            SELECT
                s.name AS skill

            FROM clean_data.job_data j

            JOIN clean_data.job_skills js
                ON j.job_id = js.job_id

            JOIN clean_data.skills s
                ON js.skill_id = s.skill_id

            WHERE j.title IN ({parameter})

            GROUP BY s.name

            HAVING COUNT(DISTINCT j.title) = %s
        ),

        role_totals AS (

            SELECT
                title,
                COUNT(*) AS total_jobs

            FROM clean_data.job_data

            WHERE title IN ({parameter})

            GROUP BY title
        ),

        skill_counts AS (

            SELECT
                j.title,
                s.name AS skill,
                COUNT(DISTINCT j.job_id) AS skill_jobs

            FROM clean_data.job_data j

            JOIN clean_data.job_skills js
                ON j.job_id = js.job_id

            JOIN clean_data.skills s
                ON js.skill_id = s.skill_id

            JOIN common_skills cs
                ON s.name = cs.skill

            WHERE j.title IN ({parameter})

            GROUP BY j.title, s.name
        )

        SELECT
            sc.title,
            sc.skill,

            ROUND(
                sc.skill_jobs * 100.0 / rt.total_jobs,
                2
            ) AS percentage

        FROM skill_counts sc

        JOIN role_totals rt
            ON sc.title = rt.title

        ORDER BY sc.skill, sc.title;
    """

    df = pd.read_sql_query(query,conn,params=(*job_roles,n,*job_roles,*job_roles,))

    return df



# ----------------skillgap analyzer_____________

def find_reuiqred_skills(field):
    engine = connect_database('clean_data')
    conn = engine.raw_connection()

    query = '''
    select s.name,count(*) as count
    from job_data j
    join job_skills js on j.job_id = js.job_id
    join skills s on js.skill_id = s.skill_id
    where j.primary_field = %s
    group by s.name
    order by count desc
    limit 10;
    '''
    df= pd.read_sql_query(query,conn,params=(field,))

    essential_skills = set(df['name'].to_list())
    return essential_skills


import numpy as np

# ---- Run ONCE when server starts, loads everything from DB ----
def build_tfidf_scores():
    engine = connect_database('clean_data')
    conn = engine.raw_connection()
    #group by skills and primary fields together
    query = '''
    SELECT j.primary_field, s.name as skill, COUNT(*) as term_freq
    FROM job_data j
    JOIN job_skills js ON j.job_id = js.job_id
    JOIN skills s ON js.skill_id = s.skill_id
    GROUP BY j.primary_field, s.name
    '''
    df = pd.read_sql_query(query, conn) 
    # count total no of primary fields
    total_fields = df['primary_field'].nunique()

    # find total no of unique fields in which it appears in
    doc_freq = df.groupby('skill')['primary_field'].nunique().reset_index()
    doc_freq.rename(columns={'primary_field': 'doc_freq'}, inplace=True)
    # then merge it into the main table . now freq of that skill & precent no of another table
    df = pd.merge(df, doc_freq, on='skill')
    df['idf'] = np.log(total_fields / df['doc_freq'])
    df['tf_idf'] = df['term_freq'] * df['idf']

    return df  

def ffind_reuiqred_skills(tfidf_df, target_field):
    target_df = tfidf_df[tfidf_df['primary_field'] == target_field]
    target_df = target_df.sort_values(by='tf_idf', ascending=False)
    essential_skills = set(target_df.head(10)['skill'].tolist())
    return essential_skills

def find_freq_skills(field : str |None= None):
    engine = connect_database("clean_data")
    conn = engine.raw_connection()
    query = '''
    SELECT j.primary_field, s.name as skill, COUNT(*) as term_freq
    FROM job_data j
    JOIN job_skills js ON j.job_id = js.job_id
    JOIN skills s ON js.skill_id = s.skill_id'''
    if field:
        query += " WHERE primary_field = %s"
    query += '''
    GROUP BY j.primary_field, s.name
    order by term_freq desc
    limit 15;
    '''
    if field:
        df = pd.read_sql_query(query,conn,params=(field,))
    else:
        df = pd.read_sql_query(query,conn)

    return df
    






# IDF = log(total_fields / how_many_fields_skill_appears_in)
    

# confidance = total_freq * idf_freq










if __name__ == '__main__':
    print(find_freq_skills('backend'))
