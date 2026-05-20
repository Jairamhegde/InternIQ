import logging
from datetime import datetime

from utils.path import JOBS_DB
from dbconnection.dbconnect import connect_database


def manage_operation(job_data):

    try:

        with connect_database(JOBS_DB) as conn:

            cur = conn.cursor()

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
                    INSERT OR IGNORE INTO jobs
                    (
                        j_title,
                        location,
                        company,
                        scraped_time,
                        postedDate,
                        minsal,
                        maxsal
                    )
                    VALUES (?, ?, ?, ?, ?, ?, ?)
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

                # Fetch generated job_id
                cur.execute(
                    '''
                    SELECT j_id
                    FROM jobs
                    WHERE j_title=? 
                    AND location=? 
                    AND company=?
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
                        INSERT OR IGNORE INTO skills(name)
                        VALUES (?)
                        ''',
                        (tech,)
                    )

                    cur.execute(
                        '''
                        SELECT s_id
                        FROM skills
                        WHERE name=?
                        ''',
                        (tech,)
                    )

                    skid = cur.fetchone()

                    skill_id = skid[0] if skid else None

                    if skill_id:

                        cur.execute(
                            '''
                            INSERT OR IGNORE INTO job_skills
                            (
                                job_id,
                                skill_id
                            )
                            VALUES (?, ?)
                            ''',
                            (
                                job_id,
                                skill_id
                            )
                        )

                # Insert snapshot
                cur.execute(
                    '''
                    INSERT OR IGNORE INTO jobSnapshot
                    (
                        job_id,
                        scraped_date
                    )
                    VALUES (?, ?)
                    ''',
                    (
                        job_id,
                        datetime.now().strftime("%Y-%m-%d")
                    )
                )

    except Exception:

        logging.exception("manage_operation failed")