import sqlite3
from datetime import datetime

from utils.path import RAWDATA_DB


def normalize(text):

    if not text:
        return None

    return " ".join(text.split()).strip().lower()


def insertRawData(job_data):

    with sqlite3.connect(RAWDATA_DB) as conn:

        cur = conn.cursor()

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
                INSERT OR IGNORE INTO JobData
                (
                    title,
                    Salary,
                    location,
                    ScrapeTime,
                    posted_date,
                    company
                )
                VALUES (?, ?, ?, ?, ?, ?)
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
                FROM JobData
                WHERE title = ?
                AND location = ?
                AND company = ?
                ''',
                (
                    title,
                    location,
                    company
                )
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
                    INSERT OR IGNORE INTO Skills(name)
                    VALUES (?)
                    ''',
                    (tech,)
                )

                cur.execute(
                    '''
                    SELECT skill_id
                    FROM Skills
                    WHERE name = ?
                    ''',
                    (tech,)
                )

                skill = cur.fetchone()

                skill_id = skill[0] if skill else None

                if skill_id:

                    cur.execute(
                        '''
                        INSERT OR IGNORE INTO JobSkills
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
                    id,
                    scraped_date
                )
                VALUES (?, ?)
                ''',
                (
                    job_id,
                    datetime.now().strftime("%Y-%m-%d")
                )
            )