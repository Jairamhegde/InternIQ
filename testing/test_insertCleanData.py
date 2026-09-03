
import pytest
from insertCleanData.insertCleanData import manage_operation
from dbconnection.dbconnect import connect_database


def test_insertCleanData():
    data = [{
        "job_title": "Backend Developer Intern",
        "location": "Bengaluru",
        "company": "TestCorp Regression",
        "scraped_time": "2026-09-02",
        "posted_date": "2026-09-01",
        "min_salary": 10000,
        "max_salary": 20000,
        "skills": ["Python", "SQL"],
        "job_link": "https://example.com/job-regression-1",
    },
     {
        "job_title": "  backend developer intern  ",   
        "location": "bengaluru",
        "company": "  TestCorp Regression",
        "scraped_time": "2026-09-02",
        "posted_date": "2026-09-01",
        "min_salary": 10000,
        "max_salary": 20000,
        "skills": ["Django"],
        "job_link": "https://example.com/job-regression-1",
    }]
    try:
        res = manage_operation(data)
        assert res is True
        db = connect_database('clean_data')
        conn = db.raw_connection()
        cur  = conn.cursor()

        query = '''
            SELECT job_id FROM job_data WHERE title = %s AND company = %s
        '''
        cur.execute(query, ("backend developer intern", "testcorp regression",))
        rows = cur.fetchall()
        assert len(rows) == 1

        cleanUp = '''
        delete from job_data
        where job_id = %s
        '''
        job_id = rows[0][0]
        cur.execute(
            """SELECT s.name FROM job_skills js
            JOIN skills s ON js.skill_id = s.skill_id
            WHERE js.job_id = %s""",
            (job_id,)
        )
        skill_names = {r[0] for r in cur.fetchall()}
        assert "python" in skill_names
        assert "django" in skill_names
    finally:
        cur.execute("DELETE FROM job_skills WHERE job_id = %s", (job_id,))
        cur.execute("DELETE FROM job_snapshot WHERE job_id = %s", (job_id,))
        cur.execute("DELETE FROM job_location WHERE job_id = %s", (job_id,))
        cur.execute("DELETE FROM job_data WHERE job_id = %s", (job_id,))
        conn.commit()
        cur.close()
        conn.close()





    



