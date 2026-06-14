
import pandas as pd
from dbconnection.dbconnect import connect_database



# ------------------------------FOR OVERALL MARKET TRENDS----

def topSkills():
    conn = connect_database("clean_data")
    query = '''
    SELECT s.name, count(*) as demand
    FROM skills s
    JOIN job_skills js ON s.skill_id = js.skill_id
    GROUP BY s.name
    ORDER BY demand DESC
    LIMIT 10;
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


# ----------------------------------------------------

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
