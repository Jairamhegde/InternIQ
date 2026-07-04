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
        conn = connect_database(search_path="raw_data")
        cur = conn.cursor()
      
        # row indices → [0]id, [1]title, [2]salary, [3]location, [4]company, [5]scrape_time, [6]posted_date
        cur.execute("SELECT * FROM job_data;")
        rows = cur.fetchall()
       
        for row in rows:
            
           
            job_id    = row[0] if row[0] is not None else None
            job_name  = " ".join(row[1].strip().split()).lower() if row[1] else None
            sal       = convertSalary(row[2]) if row[2] else (0, 0)
            min_sal   = sal[0] if sal[0] > 0 else None
            max_sal   = sal[1] if sal[1] > 0 else None
            location  = " ".join(row[3].strip().split()).lower() if row[3] else None
            company   = " ".join(row[4].strip().split()).lower() if row[4] else None
            scrape_time  = row[5] if row[5] else None
            posted_date  = row[6] if row[6] else None

            # Fetch skills for this job
            cur.execute(
                '''
                SELECT s.skill_id, s.name
                FROM job_data j
                JOIN job_skills js ON j.id = js.job_id
                JOIN skills s ON js.skill_id = s.skill_id
                WHERE j.id = %s;
                ''',
                (job_id,)
            )

            skills = cur.fetchall()
            skill_list = [
                " ".join(skill[1].lower().strip().split())
                for skill in skills
            ]

            jd = {
                "job_id"    : job_id,
                "job_title":    job_name,
                "min_salary":   min_sal,
                "max_salary":   max_sal,
                "location":     location,
                "scraped_time": scrape_time,
                "posted_date":  posted_date,
                "company":      company,
                "skills":       skill_list
            }
            job_data.append(jd)
         

        cur.close()
        conn.close()
        return job_data

    except Exception as e:
        logging.exception(f"loadData failed: {e}")
        return job_data