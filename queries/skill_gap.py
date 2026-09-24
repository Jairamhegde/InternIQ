import pandas as pd
from dbconnection.dbconnect import connect_database


# -------------------- Skill Gap Analyzer Queries --------------------

def find_reuiqred_skills(field):
    '''
    using common skills which is mentioned across the different roles of the same field
    this will help to get only the common , rather than extracting all of the skills from
    backend
    in query,first group by skill name and count distinct no of jobs in each of skill.
    then order them by count and take first 10 skills
    '''

    engine = connect_database('clean_data')
    query2 = '''
    select s.name, count (distinct j.title) as job_count
    from job_data j
    join job_skills js on j.job_id = js.job_id
    join skills s on js.skill_id = s.skill_id
    where j.primary_field = %s
    group by s.name
    order by job_count desc
    limit 10;
    '''
    df = pd.read_sql_query(query2, engine, params=(field,))

    essential_skills = set(df['name'].to_list())
    return essential_skills


def find_freq_skills(field: str | None = None) -> pd.DataFrame:
    '''
    find frequency of each skill in specified field, take top 10
    skills for analyzing the skill gap.
    '''

    engine = connect_database("clean_data")
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
        df = pd.read_sql_query(query, engine, params=(field,))
    else:
        df = pd.read_sql_query(query, engine)

    return df
