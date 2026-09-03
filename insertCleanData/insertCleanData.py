import logging
import psycopg2
from datetime import datetime
from psycopg2.extras import execute_values
from dbconnection.dbconnect import connect_database
from psycopg2.extras import execute_values
from keyword_match.dev_trend import similarity_check

def normalize(text):
    if not text:
        return None
    return " ".join(text.split()).strip().lower()


def get_loc_list(location):
    return location.split(",")



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
                    normalize(i['job_title']),
                    normalize(i['company']),
                    i['scraped_time'],
                    i['posted_date'],
                    i['min_salary'],
                    i['max_salary'],
                    check[0],
                    float(check[1]),
                    i['job_link']
                ))

        if not job_data_tuple:
            return

        # 1. Insert jobs using execute_values
        query1 = '''
            INSERT INTO job_data
            (title, company, scrape_time, posted_date, salary_min, salary_max,primary_field, field_confidence,job_link)
            VALUES %s
            ON CONFLICT(title,company, posted_date) DO NOTHING;
        '''
        execute_values(cur, query1, job_data_tuple)
        
        #Getting job id's and other details by creating a vetual table using VALUES and joining it.
        query2 = '''
            SELECT j.job_id, j.title, j.company, j.posted_date
            FROM job_data j
            JOIN (VALUES %s) AS v(title, company, posted_date)
              ON j.title = v.title
             AND j.company = v.company
             AND j.posted_date = CAST(v.posted_date AS DATE)
        '''
        
        lookup_tuples = [(t[0], t[1], t[3]) for t in job_data_tuple]
        
        # Fetch ALL job IDs (both new and existing) and overwrite job_ids
        job_ids = execute_values(cur, query2, lookup_tuples, fetch=True)

        if not job_ids:
            conn.commit()
            return
        
        job_map = {
            (job_m[1], job_m[2], str(job_m[3])): job_m[0]
            for job_m in job_ids
        }

         #build location set for batch insertion
        loc_set = set()
        for m in job_data:
            loc_str = m.get("location")
            if loc_str:
                # get_loc_list doesn't strip spaces, so we strip them here to avoid duplicates like ' NY' and 'NY'
                loc_set.update([loc.strip() for loc in get_loc_list(loc_str) if loc.strip()])

        loc_tuple = [(loc,) for loc in loc_set]

        inser_loc_query = """
        insert into locations(loc)
        values %s
        on conflict do nothing;
        """
        if loc_tuple:
            execute_values(cur,inser_loc_query,loc_tuple)

        get_location = '''
        select id,loc from locations;
        '''
        cur.execute(get_location)
        locations = cur.fetchall()
        
        # BUG FIX 1: Used row[1] and row[0] instead of locations[1]
        loc_map = {row[1]: row[0] for row in locations} 
        
        job_loc_map = []
        for k in job_data:
            # We must skip incomplete data just like we did when inserting jobs
            if not (k.get('skills') and k.get('company') and k.get('job_title')):
                continue

            # BUG FIX 2: Create the exact same normalized job_key used in job_map
            job_key = (
                normalize(k.get('job_title')),
                normalize(k.get('company')),
                str(k.get('posted_date'))
            )
            
            job_id = job_map.get(job_key)
            if not job_id:
                continue

            loc_str = k.get('location')
            if loc_str:
                location_list = [loc.strip() for loc in get_loc_list(loc_str) if loc.strip()]
                for loc in location_list:
                    loc_id = loc_map.get(loc)
                    if loc_id:
                        job_loc_map.append((job_id, loc_id))

        # BUG FIX 3: Execute values ONCE outside of the loop!
        inser_job_locations = '''
        insert into job_location(job_id,loc_id)
        values %s on conflict do nothing;
        '''
        if job_loc_map:
            execute_values(cur, inser_job_locations, job_loc_map)
            
        # 2. Extract unique skills
        skill_set = set()
        for i in job_data:
            if i.get('skills') and i.get('company') and i.get('job_title'):
                skill_set.update([normalize(s) for s in i['skills'] if s])
        
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
            
        # Build a map: (title, company, posted_date) -> job_id
        

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

            job_key = (
                normalize(j['job_title']),
                normalize(j['company']),
                str(j['posted_date'])
            )
            if job_key not in job_map:
                continue

            for skill in j['skills']:
                skill_id = skill_map.get(normalize(skill))
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
        return True

    except Exception as e:
        try:
            conn.rollback()
        except Exception:
            pass # Ignore rollback errors if connection is closed
        logging.exception(f"manage_operation failed: {e}")
        return False

    finally:
        if cur:
            cur.close()
        if conn:
            conn.close()