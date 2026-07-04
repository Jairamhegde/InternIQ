from datetime import datetime
from dbconnection.dbconnect import connect_database
from psycopg2.extras import execute_values

def normalize(text):
    if not text:
        return None
    return " ".join(text.split()).strip().lower()

def insertRawData(job_data):

    conn = connect_database(search_path="raw_data")
    cur = conn.cursor()

    try:
        
        
        job_data_tuple = [
                (
                normalize(job['job_title']),
                job['salary'],
                normalize(job['location']),
                job['scrape_time'],
                job['posted_date'],
                normalize(job['company'])
            ) 
            for job in job_data
        ]


        # Insert Job
        query1 = \
            '''
            INSERT INTO job_data
            (title, salary, location, scrape_time, posted_date, company)
            VALUES %s
            RETURNING id, title, salary, location, company
            ;
            '''
        job_ids = execute_values(cur, query1, job_data_tuple, fetch=True)

        

        #Create skill set batch to insert at once
        skill_set = set()
        for job in job_data:
            skill_set.update(job.get('tech_stack',[]))

        skill_tuple = [(skill,) for skill in skill_set]
        skill_query =\
                '''
                INSERT INTO skills (name)
                VALUES %s
                ON CONFLICT DO NOTHING;
                '''
        if skill_tuple:
            execute_values(cur,skill_query,skill_tuple)

        job_map = {
            (job_m[1],job_m[2],job_m[3],job_m[4]):job_m[0] for job_m in job_ids
        }


        cur.execute('''
        select skill_id,name from skills;
        ''')
        rows = cur.fetchall()
        skill_map = {row[1]:row[0] for row in rows}


        skill_job_map = []

        for j in job_data:
            job_tuple = (normalize(j.get('job_title')),j.get('salary'),normalize(j.get('location')),normalize(j.get('company')))

            for skill in j.get('tech_stack',[]):
                skill_id = skill_map[skill]

                job_id = job_map[job_tuple]
                skill_job_map.append((job_id,skill_id))


        
            job_skill_query = \
                '''
                INSERT INTO job_skills (job_id, skill_id)
                VALUES %s
                ON CONFLICT DO NOTHING;
                '''
        if skill_job_map:
            execute_values(cur,job_skill_query,skill_job_map)

        conn.commit()

    except Exception as e:
        conn.rollback()
        raise e
    
    finally:
        if cur:
            cur.close()
      

   