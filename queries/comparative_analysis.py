from sqlalchemy import column
import pandas as pd
from dbconnection.dbconnect import connect_database


# -------------------- Role Trend Comparison --------------------

def compare_role_trend(*roles):
    parameter = ",".join(['%s'] * len(roles))
    db = connect_database('clean_data')
    query = f'''
    select to_char(posted_date::date,'month') as month, extract(month from posted_date::date)::int as month_no,title, count(*) as postings
    from job_data
    where title in ({parameter})
    group by to_char(posted_date::date,'month'),extract(month from posted_date::date), title
    order by month_no asc;
    '''
    df = pd.read_sql_query(query, db, params=(*roles,))

    if not df.empty:
        df = (df.pivot_table(index=['month_no','month'], columns='title', values='postings', fill_value=0)
              .reset_index())

        df.drop(columns=['month_no'],inplace=True)
        
    return df


# -------------------- Common Skills Across Roles --------------------

def common_skills(job_roles) -> pd.DataFrame:
    conn = connect_database('clean_data')

    n = len(job_roles)
    if n < 1:
        return pd.DataFrame()

    parameter = ", ".join(["%s"] * n)
    query = f'''
    SELECT s.name
    FROM clean_data.job_data j
    JOIN clean_data.job_skills js ON j.job_id = js.job_id
    JOIN clean_data.skills s ON js.skill_id = s.skill_id
    WHERE j.title in ({parameter})
    GROUP BY s.name
    HAVING count(distinct j.title) = %s;
    '''
    place_holder = (*job_roles, n)

    df = pd.read_sql_query(query, conn, params=place_holder)
    return df


# -------------------- Skill Overlap Percentage --------------------

def get_percentage_ofskills(job_roles) -> pd.DataFrame:
    '''
    at first we select common skills which is overlapping in selected roles
    then we take role count of each of the role.
    then we have to find  how strongly this role is connected to overlapping skills,
    so we create job_title and skill, group them together and count the number of roles in it
    this will create[title 1 ,skill1,count]
                    [title 1 ,skill2,count]
    then we take each job grouped with these skills and find confidence percentage using
    formula (total jobs with this skill * 100 / total no of this job)
    '''

    n = len(job_roles)
    conn = connect_database('clean_data')

    parameter = ", ".join(["%s"] * n)
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

    df = pd.read_sql_query(query, conn, params=(*job_roles, n, *job_roles, *job_roles,))

    return df

if __name__ == "__main__":
        print(compare_role_trend("data engineer","data scientist"))

