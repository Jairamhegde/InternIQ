from dbconnection.dbconnect import connect_database
import pandas as pd


def Top_role():
    conn = connect_database("clean_data")
    query = '''
    SELECT title, count(*) as job_count, posted_date
    FROM job_data
    WHERE posted_date::date >= CURRENT_DATE - INTERVAL '10 days'
    GROUP BY title, posted_date
    ORDER BY job_count DESC
    LIMIT 5;
    '''
    df = pd.read_sql_query(query, conn)
    return df


def top_skill():
    conn = connect_database("clean_data")
    query = '''
    SELECT s.name as skill, count(*) as skill_count
    FROM job_data j
    JOIN job_skills js ON j.id = js.job_id
    JOIN skills s ON js.skill_id = s.skill_id
    WHERE j.posted_date::date >= CURRENT_DATE - INTERVAL '10 days'
    GROUP BY s.name
    ORDER BY skill_count DESC
    LIMIT 5;
    '''
    df = pd.read_sql_query(query, conn)
    return df


def total_opportunities():
    conn = connect_database("clean_data")
    query = '''
    SELECT count(*) as total_opportunities
    FROM job_data
    WHERE posted_date::date >= CURRENT_DATE - INTERVAL '10 days';
    '''
    df = pd.read_sql_query(query, conn)
    return df


def average_salary(role):
    conn = connect_database("clean_data")
    query = '''
    SELECT title,min(salary_min) as minimum,max(salary_max) as maximum,
    avg((salary_min+salary_max)/2.0) as average,
    count(*) as count
    from job_data
    WHERE title = %s
    GROUP BY title;
    '''
    df = pd.read_sql_query(query,conn,params=(role,))
    return df


# print(average_salary("python developer"))

