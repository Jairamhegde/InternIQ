from datetime import datetime
from dbconnection.dbconnect import connect_database
from psycopg2.extras import execute_values


JOB_QUERY = '''
    INSERT INTO job_data
    (title, salary, location, scrape_time, posted_date, company, job_link, run_id, source)
    VALUES %s
    ON CONFLICT (title, location, company, posted_date)
    DO UPDATE SET run_id = EXCLUDED.run_id
    RETURNING id, title, location, company, posted_date::text;
'''

SKILL_QUERY = '''
    INSERT INTO skills (name)
    VALUES %s
    ON CONFLICT DO NOTHING;
'''

JOB_SKILL_QUERY = '''
    INSERT INTO job_skills (job_id, skill_id)
    VALUES %s
    ON CONFLICT DO NOTHING;
'''

SNAPSHOT_QUERY = '''
    INSERT INTO job_snapshot (job_id, scraped_date)
    VALUES %s
    ON CONFLICT DO NOTHING;
'''


def insert_raw_data(job_data):
    engine = connect_database(search_path="raw_data")
    conn = engine.raw_connection()
    cur = conn.cursor()

    try:
        cur.execute("SELECT COALESCE(MAX(run_id), 0) + 1 FROM job_data;")
        run_id = cur.fetchone()[0]

        unique_jobs = {}
        for job in job_data:
            if job.get('tech_stack') and job.get('company') and job.get('job_title'):
                key = (job['job_title'], job['location'], job['company'], job['posted_date'])
                unique_jobs[key] = job

        if not unique_jobs:
            return

        job_tuples = [
            (
                job['job_title'],
                job['salary'],
                job['location'],
                job['scrape_time'],
                job['posted_date'],
                job['company'],
                job['job_link'],
                run_id,
                job.get('source', 'internshala')
            )
            for job in unique_jobs.values()
        ]
        rows = execute_values(cur, JOB_QUERY, job_tuples, fetch=True)

        if not rows:
            conn.commit()
            return

        id_by_key = {(r[1], r[2], r[3], r[4]): r[0] for r in rows}

        missing = [key for key in unique_jobs if key not in id_by_key]
        if missing:
            raise ValueError(
                f"{len(missing)} job(s) did not map to a returned id, e.g. {missing[0]}"
            )

        skill_set = {s for job in unique_jobs.values() for s in job['tech_stack'] if s}
        if skill_set:
            execute_values(cur, SKILL_QUERY, [(skill,) for skill in skill_set])

        cur.execute('SELECT skill_id, name FROM skills;')
        skill_map = {name: skill_id for skill_id, name in cur.fetchall()}

        job_skill_tuples = [
            (id_by_key[key], skill_map[skill])
            for key, job in unique_jobs.items()
            for skill in job['tech_stack']
            if skill in skill_map
        ]
        if job_skill_tuples:
            execute_values(cur, JOB_SKILL_QUERY, job_skill_tuples)

        today_date = datetime.now().strftime("%Y-%m-%d")
        snapshot_tuples = [(job_id, today_date) for job_id in id_by_key.values()]
        if snapshot_tuples:
            execute_values(cur, SNAPSHOT_QUERY, snapshot_tuples)

        conn.commit()
        return True

    except Exception as e:
        conn.rollback()
        raise e
    finally:
        if cur:
            cur.close()
        if conn:
            conn.close()
