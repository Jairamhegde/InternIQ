import re
import logging
from dbconnection.dbconnect import connect_database

def convertSalary(s: str):
    if not s:
        return 0, 0
    s = "".join(s.split()).lower()
    s = s.replace(",", "")
    currency = detect_currency(s)
    minSal, maxSal = stripedSal(s)
    minSal = currencymap(minSal, currency)
    maxSal = currencymap(maxSal, currency)
    return minSal, maxSal

def stripedSal(s: str):
    f = detect_currency(s)
    if f == "0":
        return 0, 0
    if f == "euro":
        s = s.replace("€", "")
    if f == "aed":
        s = s.replace("aed", "")
    if f == "inr":
        s = s.replace("₹", "")
        s = s.replace("inr", "")
    if f == "usd":
        s = s.replace("$", "")
    if f == "unknown":
        minsal = maxsal = 0
        s = re.findall(r'\d+', s)
        if len(s) == 1:
            minsal = maxsal = int(s[0])
        else:
            minsal, maxsal = int(s[0]), int(s[1])
        return minsal, maxsal

    if "-" in s:
        sal = re.findall(r'\d+', s)
        minsal = sal[0]
        maxsal = sal[1]
    else:
        minsal = maxsal = re.findall(r'\d+', s)[0]

    return int(minsal), int(maxsal)


def detect_currency(s):
    find = re.search(r"\d", s)
    if not find:
        return "0"
    if "₹" in s or "inr" in s:
        return "inr"
    if "$" in s:
        return "usd"
    if "€" in s:
        return "euro"
    if "aed" in s:
        return "aed"
    return "unknown"


def currencymap(number, currencyType):
    d = {
        "inr": 1,
        "usd": 90,
        "euro": 98,
        "aed": 26.13,
        "unknown": 1,
        "0": 0
    }
    return number * d[currencyType]


def loadData():
    job_data = []
    try:
        engine = connect_database(search_path="raw_data")
        conn = engine.raw_connection()
        cur = conn.cursor()

        # Fetch jobs scraped today
        cur.execute("SELECT id, title, salary, location, company, scrape_time, posted_date,job_link FROM job_data WHERE scrape_time::date = CURRENT_DATE;")
        rows = cur.fetchall()

        job_dict = {}
        for row in rows:
            job_id = row[0] if row[0] else None
            if not job_id:
                continue
                
            job_name  = " ".join(row[1].strip().split()).lower() if row[1] else None
            sal       = convertSalary(row[2]) if row[2] else (0, 0)
            location  = " ".join(row[3].strip().split()).lower() if row[3] else None
            company   = " ".join(row[4].strip().split()).lower() if row[4] else None
            
            job_dict[job_id] = {
                "job_title":    job_name,
                "min_salary":   sal[0] if sal[0] > 0 else None,
                "max_salary":   sal[1] if sal[1] > 0 else None,
                "location":     location,
                "scraped_time": row[5] if row[5] else None,
                "posted_date":  row[6] if row[6] else None,
                "company":      company,
                "skills":       [],
                "job_link" :   row[7] if  row[7] else None
            }

        # Fetch skills for jobs scraped today
        cur.execute('''
            SELECT js.job_id, s.name
            FROM job_skills js
            JOIN skills s ON js.skill_id = s.skill_id
            JOIN job_data jd ON js.job_id = jd.id
            WHERE jd.scrape_time::date = CURRENT_DATE;
        ''')
        skill_rows = cur.fetchall()

        for job_id, skill_name in skill_rows:
            if job_id in job_dict and skill_name:
                job_dict[job_id]["skills"].append(" ".join(skill_name.lower().strip().split()))

        job_data = list(job_dict.values())

        cur.close()
        conn.close()
        return job_data

    except Exception as e:
        logging.exception(f"loadData failed: {e}")
        return job_data