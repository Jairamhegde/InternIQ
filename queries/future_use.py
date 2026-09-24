"""
future_use.py
-------------
Archived queries not currently used in the backend API.
These are preserved here for potential future features, reporting, or testing purposes.
"""

import pandas as pd
from dbconnection.dbconnect import connect_database


# --------------------  Role Overview (simple) --------------------

def roles() -> pd.DataFrame:
    conn = connect_database("clean_data")
    query = '''
    SELECT title, count(*) as demand
    from clean_data.job_data
    group by title
    order by demand desc
    LIMIT 10;
    '''
    df = pd.read_sql_query(query, conn)
    return df


# -------------------- Opportunity Counts --------------------

def noOfopportunities(field: str | None = None, month: int | None = None):
    conn = connect_database()
    query = '''
    SELECT count(*) as opportunities
    FROM job_data
    '''
    parameter = []
    if field:
        query += " where primary_field = %s"
        parameter.append(field)
    if month:
        query += " and DATE_TRUNC('month', posted_date::date) = %s"
        parameter.append(field)
    df = pd.read_sql_query(query, conn, params=(tuple(parameter) if parameter else None))

    return df['opportunities'][0]


def OPPORTUNITIES():
    """Total opportunities posted in the last 10 days."""
    conn = connect_database("clean_data")
    query = '''
    SELECT count(*) as opportunities
    FROM job_data
    WHERE posted_date::date >= CURRENT_DATE - INTERVAL '10 days';
    '''
    df = pd.read_sql_query(query, conn)

    return df['opportunities'][0]


# -------------------- Role-Specific Analysis --------------------

def TopSkillsOfRole(role) -> pd.DataFrame:
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


def jobCount(job) -> pd.DataFrame:
    conn = connect_database("clean_data")
    query = '''
    SELECT count(*) as no_of_jobs
    FROM job_data
    WHERE title = %s;
    '''
    df = pd.read_sql_query(query, conn, params=(job,))

    return df


# -------------------- Skill Counts per Role --------------------

def uniqueSkills(role) -> pd.DataFrame:
    """Count of distinct skills for a given job_id."""
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


def uniqueSkillCount(role) -> pd.DataFrame:
    """Top 8 skills with their frequency for a given job title."""
    conn = connect_database("clean_data")
    query = '''
    SELECT s.name as skill, count(*) as count
    FROM job_data j
    JOIN job_skills js ON j.job_id = js.job_id
    JOIN skills s ON js.skill_id = s.skill_id
    WHERE j.title = %s
    GROUP BY s.name
    ORDER BY count(*) DESC
    LIMIT 8;
    '''
    df = pd.read_sql_query(query, conn, params=(role,))

    return df


# -------------------- Misc --------------------

def commonSkills() -> pd.DataFrame:
    """Skills shared across the top 2 job roles by occurrence."""
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


def last_scraped_time():
    """Returns the most recent scrape_time from job_data. See get_last_sync_time in recent_market_trends.py."""
    conn = connect_database("clean_data")
    query = '''
    SELECT max(scrape_time)
    FROM job_data;
    '''
    df = pd.read_sql_query(query, conn)
    return df.iloc[0, 0]
