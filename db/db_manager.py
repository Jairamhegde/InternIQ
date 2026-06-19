import logging
import psycopg2
from datetime import datetime
from dbconnection.dbconnect import connect_database

def manage_operation(job_data):
    logging.info("Opening JIT connection for manage_operation...")
    conn = connect_database(search_path="clean_data")
    cur  = conn.cursor()

    try:
        for i in job_data:

            # Safely check for required keys
            if not (
                i.get('skills')
                and i.get('company')
                and i.get('job_title')
            ):
                continue

            # 1. Insert the job WITHOUT the raw job_id. Ask Postgres to return the clean ID.
            cur.execute(
                '''
                INSERT INTO job_data
                (title, location, company, scrape_time, posted_date, salary_min, salary_max)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (title,location,company) DO NOTHING
                RETURNING job_id;
                ''',
                (
                    i['job_title'],
                    i['location'],
                    i['company'],
                    i.get('scraped_time'),
                    i.get('posted_date'),
                    i.get('min_salary'),
                    i.get('max_salary')
                )
            )

            result = cur.fetchone()

            if result:
                # The job was new, so we capture the newly generated ID
                clean_job_id = result[0] 
            else:
                # 2. It was a duplicate! Fetch the ID of the job ALREADY sitting in the database.
                cur.execute(
                    '''
                    SELECT job_id FROM job_data
                    WHERE title = %s AND location = %s AND company = %s;
                    ''',
                    (i['job_title'], i['location'], i['company'])
                )
                clean_job_id = cur.fetchone()[0]

            # Insert skills
            for techstack in i['skills']:
                tech = techstack.lower().strip()

                cur.execute(
                    '''
                    INSERT INTO skills (name)
                    VALUES (%s)
                    ON CONFLICT (name) DO NOTHING;
                    ''',
                    (tech,)
                )

                cur.execute(
                    '''
                    SELECT skill_id
                    FROM skills
                    WHERE name = %s;
                    ''',
                    (tech,)
                )

                skid     = cur.fetchone()
                skill_id = skid[0] if skid else None

                if skill_id:
                    # 3. Use the clean_job_id for your foreign keys!
                    cur.execute(
                        '''
                        INSERT INTO job_skills (job_id, skill_id)
                        VALUES (%s, %s)
                        ON CONFLICT (job_id, skill_id) DO NOTHING;
                        ''',
                        (clean_job_id, skill_id)
                    )

            # Insert snapshot
            # 4. Use the clean_job_id for the snapshot
            cur.execute(
                '''
                INSERT INTO job_snapshot (job_id, scraped_date)
                VALUES (%s, %s)
                ON CONFLICT (job_id, scraped_date) DO NOTHING;
                ''',
                (
                    clean_job_id,
                    datetime.now().strftime("%Y-%m-%d")
                )
            )

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
        raise e  # Re-raise the original error so the pipeline knows it failed

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