import logging
from datetime import datetime
from dbconnection.dbconnect import connect_database


def manage_operation(job_data):

    conn = connect_database(search_path="clean_data")
    cur  = conn.cursor()

    try:
        for i in job_data:

            if not (
                i['skills']
                and i['company']
                and i['job_title']
            ):
                continue

            # Insert job
            cur.execute(
                '''
                INSERT INTO job_data
                (title, location, company, scrape_time, posted_date, salary_min, salary_max)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT DO NOTHING;
                ''',
                (
                    i['job_title'],
                    i['location'],
                    i['company'],
                    i['scraped_time'],
                    i['posted_date'],
                    i['min_salary'],
                    i['max_salary']
                )
            )

            # Fetch generated job id
            cur.execute(
                '''
                SELECT id
                FROM job_data
                WHERE title   = %s
                AND   location = %s
                AND   company  = %s;
                ''',
                (
                    i['job_title'],
                    i['location'],
                    i['company']
                )
            )

            result = cur.fetchone()
            job_id = result[0] if result else None

            if not job_id:
                continue

            # Insert skills
            for techstack in i['skills']:

                tech = techstack.lower().strip()

                cur.execute(
                    '''
                    INSERT INTO skills (name)
                    VALUES (%s)
                    ON CONFLICT DO NOTHING;
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
                    cur.execute(
                        '''
                        INSERT INTO job_skills (job_id, skill_id)
                        VALUES (%s, %s)
                        ON CONFLICT DO NOTHING;
                        ''',
                        (job_id, skill_id)
                    )

            # Insert snapshot
            cur.execute(
                '''
                INSERT INTO job_snapshot (job_id, scraped_date)
                VALUES (%s, %s)
                ON CONFLICT DO NOTHING;
                ''',
                (
                    job_id,
                    datetime.now().strftime("%Y-%m-%d")
                )
            )

        conn.commit()
        logging.info("manage_operation completed successfully")

    except Exception:
        conn.rollback()
        logging.exception("manage_operation failed")

    finally:
        cur.close()
        conn.close()