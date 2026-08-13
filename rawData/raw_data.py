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
<<<<<<< Updated upstream
        for job in job_data:

            if not (
                job['tech_stack']
                and job['company']
                and job['job_title']
            ):
                continue

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
=======

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

        # Insert Jobs — skip duplicates, return only newly inserted rows
        query1 = '''
            INSERT INTO job_data
            (title, salary, location, scrape_time, posted_date, company)
            VALUES %s
            ON CONFLICT(title, location, company, posted_date) DO NOTHING
            RETURNING id, title, salary, location, company
            ;
        '''
        job_ids = execute_values(cur, query1, job_data_tuple, fetch=True)

        # If all jobs were duplicates, nothing to do — commit and exit
        if not job_ids:
            conn.commit()
            return

        # ---- Process skills only for newly inserted jobs ----

        # Collect all unique skills from the new jobs
        skill_set = set()
        for job in job_data:
            skill_set.update(job.get('tech_stack', []))

        skill_tuple = [(skill,) for skill in skill_set]

        skill_query = '''
            INSERT INTO skills (name)
            VALUES %s
            ON CONFLICT DO NOTHING;
        '''
        if skill_tuple:
            execute_values(cur, skill_query, skill_tuple)

        # Build a map: (title, salary, location, company) -> job_id
        # RETURNING gives: id=0, title=1, salary=2, location=3, company=4
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
                normalize(j.get('job_title')),
                j.get('salary'),
                normalize(j.get('location')),
                normalize(j.get('company'))
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
>>>>>>> Stashed changes

        conn.commit()

    except Exception as e:
        conn.rollback()
        raise e

<<<<<<< Updated upstream
   
=======
    finally:
        if cur:
            cur.close()
        if conn:
            conn.close()
>>>>>>> Stashed changes
