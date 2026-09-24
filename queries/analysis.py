
import pandas as pd
from dbconnection.dbconnect import connect_database
from datetime import datetime


# -------------------- Market Overview Queries --------------------

def topSkills(year: int | None = None, field: str | None = None, month: int | None = None) -> pd.DataFrame:
    conn = connect_database("clean_data")
    query = '''
    SELECT s.name, count(*) as demand
    FROM skills s
    JOIN job_skills js ON s.skill_id = js.skill_id
    JOIN job_data j ON js.job_id = j.job_id'''

    if isinstance(year, str) and not year.isdigit():
        field = year
        year = None

    params = []
    conditions = []

    if year:
        conditions.append("EXTRACT(year FROM j.posted_date::date) = %s")
        params.append(year)
    if field:
        conditions.append("j.primary_field = %s")
        params.append(field)
    if month:
        conditions.append("EXTRACT(month FROM j.posted_date::date) = %s")
        params.append(month)

    if conditions:
        query += " WHERE " + " AND ".join(conditions)

    query += '''
    GROUP BY s.name
    ORDER BY demand DESC
    LIMIT 6;'''

    df = pd.read_sql_query(query, conn, params=(tuple(params) if params else None))

    return df


def toproles(year: int | None = None, field: str | None = None, month: int | None = None) -> pd.DataFrame:
    conn = connect_database("clean_data")
    query = '''
    select title as role, count(*) as volume
    from job_data
    '''
    if isinstance(year, str) and not year.isdigit():
        field = year
        year = None

    params = []
    conditions = []

    if year:
        conditions.append("EXTRACT(year FROM posted_date::date) = %s")
        params.append(year)
    if field:
        conditions.append("primary_field = %s")
        params.append(field)
    if month:
        conditions.append("EXTRACT(month FROM posted_date::date) = %s")
        params.append(month)

    if conditions:
        query += " WHERE " + " AND ".join(conditions)

    query += '''
    group by title
    order by volume desc
    LIMIT 6;
    '''
    df = pd.read_sql_query(query, conn, params=(tuple(params) if params else None))

    return df


def topLocations(year: int | None = None, field: str | None = None, month: int | None = None) -> pd.DataFrame:
    conn = connect_database("clean_data")
    query = '''
    SELECT l.loc as location, count(l.loc) as count
    FROM job_data j
    JOIN job_location jl ON j.job_id = jl.job_id
    JOIN locations l ON jl.loc_id = l.id'''

    if isinstance(year, str) and not year.isdigit():
        field = year
        year = None

    params = []
    conditions = []

    if year:
        conditions.append("EXTRACT(year FROM j.posted_date::date) = %s")
        params.append(year)
    if field:
        conditions.append("j.primary_field = %s")
        params.append(field)
    if month:
        conditions.append("EXTRACT(month FROM j.posted_date::date) = %s")
        params.append(month)

    if conditions:
        query += " WHERE " + " AND ".join(conditions)

    query += '''
    GROUP BY l.loc
    ORDER BY count DESC
    LIMIT 10;
    '''
    df = pd.read_sql_query(query, conn, params=(tuple(params) if params else None))
    return df


# -------------------- Role Trends (Over Time) --------------------

def roles_trends(year: int | None = None, field: str | None = None, month: int | None = None) -> pd.DataFrame:
    query = '''
    WITH TopSkills AS (
        SELECT ss.name
        FROM job_data j
        JOIN job_skills js ON j.job_id = js.job_id
        JOIN skills ss ON js.skill_id = ss.skill_id
    '''
    params = []
    top_conditions = []

    if year:
        top_conditions.append("EXTRACT(year FROM j.posted_date::date) = %s")
        params.append(year)
    if field:
        top_conditions.append("j.primary_field = %s")
        params.append(field)
    if month:
        top_conditions.append("EXTRACT(month FROM j.posted_date::date) = %s")
        params.append(month)

    if top_conditions:
        query += " WHERE " + " AND ".join(top_conditions)

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

    ranked_conditions = []
    ranked_params = []

    if year:
        ranked_conditions.append("EXTRACT(year FROM j.posted_date::date) = %s")
        ranked_params.append(year)
    if field:
        ranked_conditions.append("j.primary_field = %s")
        ranked_params.append(field)
    if month:
        ranked_conditions.append("EXTRACT(month FROM j.posted_date::date) = %s")
        ranked_params.append(month)

    if ranked_conditions:
        query += " AND " + " AND ".join(ranked_conditions)

    params.extend(ranked_params)

    query += '''
        GROUP BY TO_CHAR(jsn.scraped_date, 'YYYY-MM-DD'), s.name
    )
    SELECT * FROM Ranked
    ORDER BY month, rank;
    '''
    conn = connect_database("clean_data")
    df = pd.read_sql_query(query, conn, params=(tuple(params) if params else None))

    return df


# -------------------- Job Postings --------------------

def job_postings(year, field: str | None = None) -> pd.DataFrame:
    conn = connect_database('clean_data')
    parameter = []
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
    df = pd.read_sql_query(query, conn, params=tuple(parameter))
    return df


def current_year_postings(year, field: str | None = None, month: int | None = None):
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
    if month:
        query += " and EXTRACT(month FROM posted_date::date) = %s"
        parameter.append(month)

    df = pd.read_sql_query(query, conn, params=tuple(parameter))
    return df.iloc[0]['job_postings']


# -------------------- Top Hiring Companies --------------------

def top_hiring_company(year: int = datetime.now().year, field: str = None, month: int | None = None) -> pd.DataFrame:
    '''
    get most hiring company in current year
    '''
    params = [year]
    db = connect_database('clean_data')
    query = '''
    select company, count(*) as count, string_agg(distinct title, ', ') as jobs
    from job_data
    where extract(year from posted_date::date) = %s '''
    if field:
        query += " AND primary_field = %s "
        params.append(field)
    if month:
        query += " and extract(month from posted_date::date) = %s"
        params.append(month)

    query += '''
    group by company
    order by count desc
    limit 10;
    '''
    df = pd.read_sql_query(query, db, params=tuple(params))
    return df


if __name__ == '__main__':
    print(toproles(2026, None,7))
