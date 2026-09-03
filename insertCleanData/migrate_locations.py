import logging
from dbconnection.dbconnect import connect_database
from psycopg2.extras import execute_values

logging.basicConfig(level=logging.INFO)

def get_loc_list(location):
    if not location:
        return []
    return [l.strip() for l in location.split(",") if l.strip()]

def migrate_locations():
    engine = connect_database(search_path="clean_data")
    conn = engine.raw_connection()
    cur = conn.cursor()

    try:
        logging.info("Starting location migration...")
        
        # 1. Fetch all existing jobs and their locations
        cur.execute("SELECT job_id, location FROM job_data WHERE location IS NOT NULL")
        jobs = cur.fetchall()
        
        logging.info(f"Found {len(jobs)} jobs to process.")
        
        if not jobs:
            logging.info("No jobs to migrate.")
            return

        # 2. Extract unique locations
        loc_set = set()
        for job_id, location_str in jobs:
            loc_set.update(get_loc_list(location_str))
            
        loc_tuple = [(loc,) for loc in loc_set]
        
        # 3. Insert unique locations into the locations table
        if loc_tuple:
            inser_loc_query = """
            INSERT INTO locations(loc)
            VALUES %s
            ON CONFLICT DO NOTHING;
            """
            execute_values(cur, inser_loc_query, loc_tuple)
            logging.info(f"Processed {len(loc_tuple)} unique locations.")
            
        # 4. Fetch the IDs of all locations to map them
        cur.execute('SELECT id, loc FROM locations;')
        locations = cur.fetchall()
        loc_map = {row[1]: row[0] for row in locations}
        
        # 5. Build the job_location pairs
        job_loc_map = []
        for job_id, location_str in jobs:
            location_list = get_loc_list(location_str)
            for loc in location_list:
                loc_id = loc_map.get(loc)
                if loc_id:
                    job_loc_map.append((job_id, loc_id))
                    
        # 6. Insert into job_location junction table
        if job_loc_map:
            inser_job_locations = '''
            INSERT INTO job_location(job_id, loc_id)
            VALUES %s 
            ON CONFLICT DO NOTHING;
            '''
            execute_values(cur, inser_job_locations, job_loc_map)
            logging.info(f"Mapped {len(job_loc_map)} job_location relationships.")
            
        conn.commit()
        logging.info("Migration completed successfully!")
        
      

    except Exception as e:
        conn.rollback()
        logging.error(f"Migration failed: {e}")
    finally:
        cur.close()
        conn.close()

if __name__ == "__main__":
    migrate_locations()
