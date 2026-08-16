import logging
from datetime import datetime
from dbconnection.dbconnect import connect_database
from psycopg2.extras import execute_values
from keyword_match.dev_trend import similarity_check
def manage_operation(job_data):

    engine = connect_database(search_path="clean_data")
    conn = engine.raw_connection()
    cur  = conn.cursor()

    try:
        # Build job tuples
        job_data_tuple = []
        for i in job_data:
            job_title = i.get('job_title','')
            skills_set = i.get('skills',[])
            check = similarity_check(job_title,job_title,skills_set)

            if i.get('skills') and i.get('company') and i.get('job_title'):
                job_data_tuple.append((
                    i['job_title'],
                    i['location'],
                    i['company'],
                    i['scraped_time'],
                    i['posted_date'],
                    i['min_salary'],
                    i['max_salary'],
                    check[0],
                    float(check[1])
                ))

        

        if not job_data_tuple:
            return

        # 1. Insert jobs using execute_values
        query1 = '''
            INSERT INTO job_data
            (title, location, company, scrape_time, posted_date, salary_min, salary_max,primary_field, field_confidence)
            VALUES %s
            ON CONFLICT DO NOTHING
            RETURNING job_id, title, location, company;
        '''
        job_ids = execute_values(cur, query1, job_data_tuple, fetch=True)
        
        if not job_ids:
            conn.commit()
            return
            
        # 2. Extract unique skills
        skill_set = set()
        for i in job_data:
            if i.get('skills') and i.get('company') and i.get('job_title'):
                skill_set.update([s.lower().strip() for s in i['skills'] if s])
        
        skill_set = {s for s in skill_set if s}
        skill_tuple = [(skill,) for skill in skill_set]
        
        # 3. Insert skills
        skill_query = '''
            INSERT INTO skills (name)
            VALUES %s
            ON CONFLICT DO NOTHING;
        '''
        if skill_tuple:
            execute_values(cur, skill_query, skill_tuple)
            
        # Build a map: (title, location, company) -> job_id
        # RETURNING gives: job_id=0, title=1, location=2, company=3
        job_map = {
            (job_m[1], job_m[2], job_m[3]): job_m[0]
            for job_m in job_ids
        }

        # Fetch all skill name -> skill_id mappings
        cur.execute('SELECT skill_id, name FROM skills;')
        skill_map = {row[1]: row[0] for row in cur.fetchall()}
        
        # Build job_skills pairs for batch insert
        job_skill_query = '''
            INSERT INTO job_skills (job_id, skill_id)
            VALUES %s
            ON CONFLICT DO NOTHING;
        '''
        skill_job_map = []
        for j in job_data:
            if not (j.get('skills') and j.get('company') and j.get('job_title')):
                continue
                
            job_key = (j['job_title'], j['location'], j['company'])
            if job_key not in job_map:
                continue

            for skill in j['skills']:
                skill_id = skill_map.get(skill.lower().strip())
                if skill_id is None:
                    continue
                skill_job_map.append((job_map[job_key], skill_id))

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
        logging.info("manage_operation completed successfully")

    except Exception as e:
        try:
            conn.rollback()
        except Exception:
            pass # Ignore rollback errors if connection is closed
        logging.exception(f"manage_operation failed: {e}")

    finally:
        if cur:
            cur.close()
        if conn:
            conn.close()