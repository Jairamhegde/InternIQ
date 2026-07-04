import logging
import psycopg2
from datetime import datetime
from psycopg2.extras import execute_values
from dbconnection.dbconnect import connect_database

def manage_operation(job_data):
    logging.info("Opening JIT connection for manage_operation...")
    conn = connect_database(search_path="clean_data")
  

    cur  = conn.cursor()

    try:
        job_tuple = {}
        for job in job_data:
            if job.get('job_title') and job.get("location") and job.get("company"):
                key = (
                    job.get('job_title'),
                    job.get("location") ,
                    job.get("company")
                )
                values = \
                (
                job['job_title'],
                job['location'],
                job['company'],
                job.get('scraped_time'),
                job.get('posted_date'),
                job.get('min_salary'),
                job.get('max_salary')
                )
                job_tuple[key] = values

        

        insert_to_job = \
            '''
                INSERT INTO job_data
                (title, location, company, scrape_time, posted_date, salary_min, salary_max)
                VALUES %s
                ON CONFLICT (title,location,company) 
                DO UPDATE
                set title = EXCLUDED.title
                RETURNING job_id,title,company,location;
            '''
        # Insert all the jobs at once
        job_rows = execute_values(cur,insert_to_job,list(job_tuple.values()),fetch=True)
        print("Inserted the data into the table once")
        job_data_map = {(row[1],row[3],row[2]):row[0] for row in job_rows}


        # Insert all skills at once
        skill_set = set()
        for i in job_data:
            skill_set.update(i.get('skills',[]))

        skill_tuple = [(skill,) for skill in skill_set]

        skill_insert = \
        '''
        INSERT INTO skills (name)
        VALUES %s
        ON CONFLICT (name) DO NOTHING;
        '''
        if skill_tuple:
            execute_values(cur,skill_insert,skill_tuple)

       
        #Create skill map
        cur.execute(
            "select skill_id,name from skills where name = any(%s);",(list(skill_set),)
        )
        sk_row = cur.fetchall()
        skillmap = {row[1]:row[0] for row in sk_row}

        
        job_skill_map = set()
        for j in job_data:
            if j.get('job_title') and j.get('location') and j.get('company') and j.get('skills'):
                job_id = job_data_map[
                    (j['job_title'],j['location'],j['company'])
                ]

                for skill in j['skills']:
                    skill_id = skillmap[skill]
                    job_skill_map.add(
                        (job_id,skill_id)
                    )
        insert_to_jobskill = \
            '''
            INSERT INTO job_skills (job_id, skill_id)
            VALUES %s
            ON CONFLICT (job_id, skill_id) DO NOTHING;
            '''
        execute_values(cur,insert_to_jobskill,job_skill_map)

        # Insert snapshot
        # 4. Use the clean_job_id for the snapshot
        today = datetime.now().strftime('%Y-%m-%d')
        snapshot_tuple = [
            (jobid,today)
            for jobid in job_data_map.values()
        ]
        
        snapshot_query = '''
      
            INSERT INTO job_snapshot (job_id, scraped_date)
            VALUES %s
            ON CONFLICT (job_id, scraped_date) DO NOTHING;
        '''
        execute_values(cur,snapshot_query,snapshot_tuple)
        
        conn.commit()
       
        logging.info("manage_operation completed successfully")

    except Exception as e:
        logging.exception("manage_operation failed during execution")
        
        # Safely attempt rollback, but catch the error if the connection is already dead
        try:
            if conn:
                conn.rollback()
                logging.info("Rollback executed successfully.")
        except (psycopg2.InterfaceError, psycopg2.OperationalError):
            logging.warning("Could not execute rollback; the database connection was already closed by the server.")
        raise

    finally:
        # Safely close cursor and connection, ignoring errors if they are already dead
        if cur:
            try:
                cur.close()
            except Exception:
                pass
        if conn:
            try:
                conn.close()
            except Exception:
                pass