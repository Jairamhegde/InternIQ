from datetime import datetime
from dbconnection.dbconnect import connect_database
from psycopg2.extras import execute_values


def insertRawData(job_data):
    engine = connect_database(search_path="raw_data")
    
    # Extract the raw psycopg2 connection from the SQLAlchemy engine
    conn = engine.raw_connection()
    cur = conn.cursor()

    try:
        job_data_tuple = [
            (
                job['job_title'],
                job['salary'],
                job['location'],
                job['scrape_time'],
                job['posted_date'],
                job['company'],
                job['job_link']
            )
            for job in job_data
            if job.get('tech_stack') and job.get('company') and job.get('job_title')
        ]

        if not job_data_tuple:
            return

        # Insert Jobs — allow duplicates, return all inserted rows
        query1 = '''
            INSERT INTO job_data
            (title, salary, location, scrape_time, posted_date, company,job_link)
            VALUES %s
            RETURNING id, title, salary, location, company
            ;
        '''
        job_ids = execute_values(cur, query1, job_data_tuple, fetch=True)

        # If no jobs were inserted, nothing to do — commit and exit
        if not job_ids:
            conn.commit()
            return


        # Collect all unique skills from the new jobs
        skill_set = set()
        for job in job_data:
            skill_set.update([s for s in job.get('tech_stack', []) if s])
            
        skill_set = {s for s in skill_set if s} # Remove empty

        skill_tuple = [(skill,) for skill in skill_set]

        skill_query = '''
            INSERT INTO skills (name)
            VALUES %s
            ON CONFLICT DO NOTHING;
        '''
        if skill_tuple:
            execute_values(cur, skill_query, skill_tuple)

        #building map
        job_map = {
            (job_m[1], job_m[2], job_m[3], job_m[4]): job_m[0]
            for job_m in job_ids
        }

        # Fetch all skill name -> skill_id mappings
        cur.execute('SELECT skill_id, name FROM skills;')
        rows = cur.fetchall()
        skill_map = {row[1]: row[0] for row in rows}

        # Build job_skills pairs for batch insert
        job_skill_query = '''
            INSERT INTO job_skills (job_id, skill_id)
            VALUES %s
            ON CONFLICT DO NOTHING;
        '''
        skill_job_map = []
        for j in job_data:
            job_tuple = (
                j.get('job_title'),
                j.get('salary'),
                j.get('location'),
                j.get('company')
            )
            if job_tuple not in job_map:
                continue  # skip if this job was a duplicate (not newly inserted)

            for skill in j.get('tech_stack', []):
                skill_id = skill_map.get(skill)
                if skill_id is None:
                    continue
                job_id = job_map[job_tuple]
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
        snapshot_tuples = [(job_m[0], today_date) for job_m in job_ids]
        
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
