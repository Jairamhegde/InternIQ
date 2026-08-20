import pandas as pd
from dbconnection.dbconnect import connect_database


def Top_role() -> pd.DataFrame:
    """Fetches the top 5 most demanded roles in the last 10 days."""
    conn = connect_database("clean_data")
    query = '''
    SELECT title, COUNT(*) as job_count
    FROM job_data
    WHERE posted_date::date >= CURRENT_DATE - INTERVAL '10 days'
    GROUP BY title
    ORDER BY job_count DESC
    LIMIT 5;
    '''
    df = pd.read_sql_query(query, conn)
    return df


def previous_top_role() -> pd.DataFrame:
    """Fetches the top 5 most demanded roles in the previous 10-20 day window."""
    conn = connect_database("clean_data")
    query = '''
    SELECT title, COUNT(*) as job_count
    FROM job_data
    WHERE posted_date::date >= CURRENT_DATE - INTERVAL '20 days'
      AND posted_date::date < CURRENT_DATE - INTERVAL '10 days'
    GROUP BY title
    ORDER BY job_count DESC
    LIMIT 5;
    '''
    df = pd.read_sql_query(query, conn)
    return df


def top_skill() -> pd.DataFrame:
    """Fetches the top 5 most in-demand skills in the last 10 days."""
    conn = connect_database("clean_data")
    query = '''
    SELECT s.name as skill, COUNT(*) as skill_count
    FROM job_data j
    JOIN job_skills js ON j.job_id = js.job_id
    JOIN skills s ON js.skill_id = s.skill_id
    WHERE j.posted_date::date >= CURRENT_DATE - INTERVAL '10 days'
    GROUP BY s.name
    ORDER BY skill_count DESC
    LIMIT 5;
    '''
    df = pd.read_sql_query(query, conn)
    return df


def total_opportunities() -> pd.DataFrame:
    """Fetches the total number of job opportunities posted in the last 10 days."""
    conn = connect_database("clean_data")
    query = '''
    SELECT COUNT(*) as total_opportunities
    FROM job_data
    WHERE posted_date::date >= CURRENT_DATE - INTERVAL '10 days';
    '''
    df = pd.read_sql_query(query, conn)
    return df


def previous_total_opportunities() -> pd.DataFrame:
    """Fetches the total number of job opportunities posted in the previous 10-20 day window."""
    conn = connect_database("clean_data")
    query = '''
    SELECT COUNT(*) as total_opportunities
    FROM job_data
    WHERE posted_date::date >= CURRENT_DATE - INTERVAL '20 days'
      AND posted_date::date < CURRENT_DATE - INTERVAL '10 days';
    '''
    df = pd.read_sql_query(query, conn)
    return df


def average_salary(role: str) -> pd.DataFrame:
    """Calculates the minimum, maximum, and average salary for a specific role."""
    conn = connect_database("clean_data")
    query = '''
    SELECT title, 
           MIN(salary_min) as minimum, 
           MAX(salary_max) as maximum,
           AVG((salary_min + salary_max) / 2.0) as average,
           COUNT(*) as count
    FROM job_data
    WHERE title = %s
    GROUP BY title;
    '''
    df = pd.read_sql_query(query, conn, params=(role,))
    return df


def recenttopLocations(field: str | None = None) -> pd.DataFrame:
    """Fetches the top 10 locations with the most job postings in the last 10 days."""
    conn = connect_database("clean_data")
    
    query = '''
    SELECT location, COUNT(location) as count
    FROM job_data
    WHERE posted_date::date >= CURRENT_DATE - INTERVAL '10 days'
    '''
    
    params = []
    if field:
        query += " AND primary_field = %s"
        params.append(field)
        
    query += '''
    GROUP BY location
    ORDER BY count DESC
    LIMIT 10;
    '''
    
    df = pd.read_sql_query(query, conn, params=(tuple(params) if params else None))
    return df


def recent_job_postings() -> pd.DataFrame:
    """Fetches the 10 most recent job postings from the last 10 days."""
    conn = connect_database('clean_data')
    query = '''
    SELECT title, company, job_link, posted_date
    FROM job_data
    WHERE posted_date::date >= CURRENT_DATE - INTERVAL '10 days'
    ORDER BY posted_date DESC
    LIMIT 10;
    '''
    df = pd.read_sql_query(query, conn)
    return df


if __name__ == '__main__':
    pass
