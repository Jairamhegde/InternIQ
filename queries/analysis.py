
import pandas as pd
from dbconnection.dbconnect import connect_database
from datetime import datetime


# ------------------------------FOR OVERALL MARKET TRENDS----

def topSkills():
    conn = connect_database("clean_data")
    query = '''
    SELECT s.name, count(*) as demand
    FROM skills s
    JOIN job_skills js ON s.skill_id = js.skill_id
    GROUP BY s.name
    ORDER BY demand DESC
    LIMIT 6;
    '''
    df = pd.read_sql_query(query, conn)

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

def toproles():
    conn = connect_database("clean_data")
    query = '''
    select title as role,count(*) as volume
    from job_data
    group by title
    order by  volume desc
    LIMIT 6;
    '''
    df = pd.read_sql_query(query, conn)

    return df




def noOfopportunities():
    conn = connect_database()
    query = '''
    SELECT count(*) as opportunities
    FROM job_data;
    '''
    df = pd.read_sql_query(query, conn)

    return df['opportunities'][0]


def topLocations():
    conn = connect_database("clean_data")
    query = '''
    SELECT j.location, count(j.location) as count
    FROM job_data j
    GROUP BY j.location
    ORDER BY count DESC
    LIMIT 10;
    '''
    df = pd.read_sql_query(query, conn)

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


def roles_trends():
    query = '''
    WITH TopSkills AS (
        SELECT ss.name
        FROM job_data j
        JOIN job_skills js ON j.job_id = js.job_id
        JOIN skills ss ON js.skill_id = ss.skill_id
        GROUP BY ss.name
        ORDER BY count(*) DESC
        LIMIT 4
    ),
    Ranked AS (
        SELECT
            TO_CHAR(jsn.scraped_date, 'DD') AS month,
            s.name,
            count(*) AS jobCount,
            RANK() OVER (
                PARTITION BY TO_CHAR(jsn.scraped_date, 'DD')
                ORDER BY count(*) DESC
            ) AS rank
        FROM "job_snapshot" jsn
        JOIN job_data j ON jsn.job_id = j.job_id
        JOIN job_skills js ON j.job_id = js.job_id
        JOIN skills s ON js.skill_id = s.skill_id
        WHERE s.name IN (SELECT name FROM TopSkills)
        GROUP BY TO_CHAR(jsn.scraped_date, 'DD'), s.name
    )
    SELECT * FROM Ranked
    ORDER BY month, rank;
    '''
    conn = connect_database("clean_data")
    df = pd.read_sql_query(query, conn)

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

def job_postings(year):
    conn = connect_database('clean_data')
    query = '''
    SELECT 
    TO_CHAR( posted_date::date,'month') AS month,
    COUNT(*) AS jobs
    FROM clean_data.job_data
    WHERE EXTRACT(year from posted_date::date) = %s
    GROUP BY TO_CHAR( posted_date::date,'month')
    ORDER BY min(extract(month from posted_date::date)) asc;
    '''
    df = pd.read_sql_query(query,conn,params=(year,))
    return df

def current_year_postings(year):
    conn = connect_database('clean_data')
    query = '''
    select count(*) as job_postings
    from job_data
    where extract(year from posted_date::date) = %s
    '''
    df = pd.read_sql_query(query,conn,params=(year,))
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
    












if __name__ == '__main__':
    print(get_percentage_ofskills(['full stack developer','data scientist','data engineer']))
