import pandas as pd
from datetime import datetime
from dbconnection.dbconnect import connect_database


# -------------------- Total Postings For A Role --------------------

def role_total_postings(role: str) -> int:
    '''
    returns how many postings have been recorded for the given role.
    '''
    conn = connect_database('clean_data')
    query = '''
    SELECT COUNT(*) AS total_postings
    FROM clean_data.job_data
    WHERE title = %s;
    '''
    df = pd.read_sql_query(query, conn, params=(role,))
    return int(df.iloc[0]['total_postings'])


# -------------------- Average Salary For A Role --------------------

def role_average_salary(role: str) -> float | None:
    '''
    returns the average salary for the role, using the midpoint of
    salary_min and salary_max for every posting.
    returns None when no posting of this role lists a salary.
    '''
    conn = connect_database('clean_data')
    query = '''
    SELECT ROUND(AVG((salary_min + salary_max) / 2.0)) AS average_salary
    FROM clean_data.job_data
    WHERE title = %s;
    '''
    df = pd.read_sql_query(query, conn, params=(role,))
    average_salary = df.iloc[0]['average_salary']

    if pd.isna(average_salary):
        return None
    return float(average_salary)


# -------------------- Top Skills For A Role --------------------

def role_top_skills(role: str, limit: int = 5) -> pd.DataFrame:
    '''
    groups the role's postings by title and skill, and returns the skills
    mentioned in the most postings for that role.
    '''
    conn = connect_database('clean_data')
    query = '''
    SELECT j.title AS role,
           s.name AS skill,
           COUNT(*) AS skill_count
    FROM clean_data.job_data j
    JOIN clean_data.job_skills js ON j.job_id = js.job_id
    JOIN clean_data.skills s ON js.skill_id = s.skill_id
    WHERE j.title = %s
    GROUP BY j.title, s.name
    ORDER BY skill_count DESC
    LIMIT %s;
    '''
    df = pd.read_sql_query(query, conn, params=(role, limit))
    return df


# -------------------- Monthly Postings For A Role --------------------

def role_monthly_postings(role: str, year: int | None = None) -> pd.DataFrame:
    '''
    returns the number of postings for the role in each month of the given year.
    uses the current year when no year is given.
    '''
    if year is None:
        year = datetime.now().year

    conn = connect_database('clean_data')
    query = '''
    SELECT TRIM(TO_CHAR(posted_date::date, 'Month')) AS month,
           EXTRACT(month FROM posted_date::date)::int AS month_no,
           COUNT(*) AS postings
    FROM clean_data.job_data
    WHERE title = %s
      AND EXTRACT(year FROM posted_date::date) = %s
    GROUP BY TRIM(TO_CHAR(posted_date::date, 'Month')),
             EXTRACT(month FROM posted_date::date)
    ORDER BY month_no ASC;
    '''
    df = pd.read_sql_query(query, conn, params=(role, year))
    return df


# -------------------- Full Role Details --------------------

def role_details(role: str) -> dict:
    '''
    collects everything about one role:
    total postings, average salary, its top 5 skills and its monthly postings this year.
    '''
    total_postings = role_total_postings(role)
    average_salary = role_average_salary(role)
    top_skills = role_top_skills(role)
    monthly_postings = role_monthly_postings(role)

    details = {
        "role": role,
        "total_postings": total_postings,
        "average_salary": average_salary,
        "top_skills": top_skills,
        "monthly_postings": monthly_postings,
    }
    return details


if __name__ == "__main__":
    result = role_details("data engineer")
    print("Total postings:", result["total_postings"])
    print("Average salary:", result["average_salary"])
    print(result["top_skills"])
    print(result["monthly_postings"])
