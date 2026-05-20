import pandas as pd
import os
from extract.extractor import scrape_data
from utils.path import RAWDATA_DB
from utils.path import JOBS_DB
from utils.path import TEST_DB
import sqlite3
import re
from datetime import datetime
import logging
from dbconnection.dbconnect import connect_database


def convertSalary(s:str):
    minSal = 0
    maxSal = 0
    if not s:
        return 0,0
    
    s = "".join(s.split()).lower()
    s = s.replace(",","")
    currency = detect_currency(s)
    minSal,maxSal = stripedSal(s)
    minSal = currencymap(minSal,currency)
    maxSal = currencymap(maxSal,currency)

    return minSal,maxSal
    
def stripedSal(s:str):

    f = detect_currency(s)
    if f == "0":
        return 0,0
    if f == "euro":
        s = s.replace("€","")
    if f == "aed":
         s = s.replace("aed","")
    if f == "inr":
         s = s.replace("₹","")
         s = s.replace("inr","")
    if f == "usd":
         s = s.replace("$","")
    if f == "unknown":
        minsal = maxsal = 0
        s = re.findall(r'\d+',s)
        if len(s) == 1:
            minsal = maxsal = int(s[0])
        else:
            minsal,maxsal = int(s[0]),int(s[1])
        return minsal,maxsal
    
    if "-" in s:
        sal = re.findall(r'\d+',s)
        minsal = sal[0]
        maxsal = sal[1]
    else: 
        minsal = maxsal = re.findall(r'\d+',s)[0]
    minsal = int(minsal)
    maxsal = int(maxsal)
    return minsal,maxsal
    
def detect_currency(s):
    
    find = re.search(r"\d",s)
    if not find:
        return "0"
    else:
        if "₹" in s  or "inr" in s:
            return "inr"
        if "$" in s:
            return "usd"
        if "€" in s:
            return "euro"
        if "aed" in s:
            return "aed"
        else:
            return "unknown"
def currencymap(number,currencyType):
    d = {
        "inr":1,
        "usd":90,
        "euro":98,
        "aed":26.13,
        "unknown":1,
        "0":0
    }
    return number * d[currencyType] 

def loadData():

    job_data = []

    try:

        with connect_database(RAWDATA_DB) as connRaw:

            cur1 = connRaw.cursor()

            cur1.execute("SELECT * FROM jobData")

            rows = cur1.fetchall()

            for row in rows:

                jobId = row[0] if row[0] else None

                jobName = (
                    " ".join(row[1].strip().split()).lower()
                    if row[1]
                    else None
                )

                sal = convertSalary(row[2]) if row[2] else (0, 0)

                minsal = sal[0] if sal[0] > 0 else None
                maxsal = sal[1] if sal[1] > 0 else None

                skill_list = []

                cur1.execute(
                    '''
                    SELECT s.skill_id, s.name
                    FROM JobData j
                    JOIN JobSkills jb ON j.id = jb.job_id
                    JOIN Skills s ON jb.skill_id = s.skill_id
                    WHERE j.id = ?
                    ''',
                    (jobId,)
                )

                skills = cur1.fetchall()

                for skill in skills:

                    skill_list.append(
                        " ".join(skill[1].lower().strip().split())
                    )

                location = (
                    " ".join(row[3].strip().split()).lower()
                    if row[3]
                    else None
                )

                scrape_date = row[4] if row[4] else None
                posted_date = row[5] if row[5] else None

                company = (
                    " ".join(row[6].strip().split()).lower()
                    if row[6]
                    else None
                )

                jd = {
                    "job_title": jobName,
                    "min_salary": minsal,
                    "max_salary": maxsal,
                    "location": location,
                    "scraped_time": scrape_date,
                    "posted_date": posted_date,
                    "company": company,
                    "skills": skill_list
                }

                job_data.append(jd)

        return job_data

    except Exception as e:

        logging.exception(f"loadData failed: {e}")

        return job_data
    

        
       


