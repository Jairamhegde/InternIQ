from datetime import datetime
from dbconnection.dbconnect import connect_database

def normalize(text):
    if not text:
        return None
    return " ".join(text.split()).strip().lower()

def insertRawData(job_data):

    conn = connect_database(search_path="raw_data")
    cur = conn.cursor()

    try:
        
        
        for job in job_data:

            

            title = normalize(job['job_title'])
            company = normalize(job['company'])
            location = normalize(job['location'])

            # Insert Job
            cur.execute(
                '''
                INSERT INTO job_data
                (title, salary, location, scrape_time, posted_date, company)
                VALUES (%s, %s, %s, %s, %s, %s)
                ON CONFLICT DO NOTHING;
                ''',
                (
                    title,
                    job['salary'],
                    location,
                    job['scrape_time'],
                    job['posted_date'],
                    company
                )
            )

            # Fetch job_id
            cur.execute(
                '''
                SELECT id
                FROM job_data
                WHERE title = %s
                AND location = %s
                AND company = %s;
                ''',
                (title, location, company)
            )

            result = cur.fetchone()
            job_id = result[0] if result else None

            if not job_id:
                continue

            # Insert skills
            for tech in job['tech_stack']:

                tech = normalize(tech)

                if not tech:
                    continue

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

                skill = cur.fetchone()
                skill_id = skill[0] if skill else None

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

    except Exception as e:
        conn.rollback()
        raise e
    
    finally:
        if cur:
            cur.close()

   