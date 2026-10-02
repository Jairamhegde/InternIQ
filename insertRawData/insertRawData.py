from sqlalchemy.orm import query
from datetime import datetime
from dbconnection.dbconnect import connect_database
from psycopg2.extras import execute_values


def insertRawData(job_data):
    engine = connect_database(search_path="raw_data")

    # Extract the raw psycopg2 connection from the SQLAlchemy engine
    conn = engine.raw_connection()
    cur = conn.cursor()

    try:
        cur.execute("SELECT COALESCE(MAX(run_id), 0) + 1 FROM job_data;")
        run_id = cur.fetchone()[0]

        # Keep only valid jobs; this list stays aligned with job_data_tuple
        valid_jobs = [
            job for job in job_data
            if job.get('tech_stack') and job.get('company') and job.get('job_title')
        ]

        job_data_tuple = [
            (
                job['job_title'],
                job['salary'],
                job['location'],
                job['scrape_time'],
                job['posted_date'],
                job['company'],
                job['job_link'],
                run_id
            )
            for job in valid_jobs
        ]

        if not job_data_tuple:
            return

        # Insert Jobs — allow duplicates, return ids in insertion order
        query1 = '''
            INSERT INTO job_data
            (title, salary, location, scrape_time, posted_date, company, job_link, run_id)
            VALUES %s
            RETURNING id
            ;
        '''
        job_ids = execute_values(cur, query1, job_data_tuple, fetch=True)

        # If no jobs were inserted, nothing to do — commit and exit
        if not job_ids:
            conn.commit()
            return

        # Safety check: one returned id per inserted row
        if len(job_ids) != len(valid_jobs):
            raise ValueError(
                f"Row count mismatch: inserted {len(job_ids)}, expected {len(valid_jobs)}"
            )

        # Collect all unique skills from the new jobs
        skill_set = set()
        for job in valid_jobs:
            skill_set.update(s for s in job['tech_stack'] if s)

        skill_tuple = [(skill,) for skill in skill_set]

        skill_query = '''
            INSERT INTO skills (name)
            VALUES %s
            ON CONFLICT DO NOTHING;
        '''
        if skill_tuple:
            execute_values(cur, skill_query, skill_tuple)

        # Fetch all skill name -> skill_id mappings
        cur.execute('SELECT skill_id, name FROM skills;')
        skill_map = {row[1]: row[0] for row in cur.fetchall()}

        # Build job_skills pairs by position
        job_skill_query = '''
            INSERT INTO job_skills (job_id, skill_id)
            VALUES %s
            ON CONFLICT DO NOTHING;
        '''
        skill_job_map = []
        for job, (job_id,) in zip(valid_jobs, job_ids):
            for skill in job['tech_stack']:
                skill_id = skill_map.get(skill)
                if skill_id is None:
                    continue
                skill_job_map.append((job_id, skill_id))

        if skill_job_map:
            execute_values(cur, job_skill_query, skill_job_map)

        # Build job_snapshot pairs
        snapshot_query = '''
            INSERT INTO job_snapshot (job_id, scraped_date)
            VALUES %s
            ON CONFLICT DO NOTHING;
        '''
        today_date = datetime.now().strftime("%Y-%m-%d")
        snapshot_tuples = [(row[0], today_date) for row in job_ids]

        if snapshot_tuples:
            execute_values(cur, snapshot_query, snapshot_tuples)

        conn.commit()

    except Exception as e:
        conn.rollback()
        raise e
    finally:
        if cur:
            cur.close()
        if conn:
            conn.close()