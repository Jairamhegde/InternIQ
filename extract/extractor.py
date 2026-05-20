from datetime import datetime, timedelta
import logging
import re
import pandas as pd


def dateFromtext(i):

    match = re.search(r"(\d+)\s(\w+)\sago", i)

    if not match:
        return None

    value = int(match.group(1))
    measure = match.group(2)

    if measure == "day" or measure == "days":
        date = (datetime.now() - timedelta(days=value)).strftime("%Y-%m-%d")
        return date

    if measure == "week" or measure == "weeks":
        date = (datetime.now() - timedelta(weeks=value)).strftime("%Y-%m-%d")
        return date

    return None


def scrape_data(soup):

    job_data = []

    try:

        job_card = soup.find_all('div', class_="internship_meta experience_meta")

        if job_card:

            for job in job_card:

                postedtime_tag = job.select_one("div.color-labels span")
                posted_time = postedtime_tag.text if postedtime_tag else None

                skills_tag = job.find_all('div', class_="skill_container")
                skills = skills_tag if skills_tag else None

                job_tag = job.find('a', id='job_title')
                jobb = job_tag.text if job_tag else None

                company_tag = job.find('p', class_="company-name")
                comp = company_tag.text if company_tag else None

                status_tag = job.find('div', class_="actively-hiring-badge")
                status = status_tag.text if status_tag else None

                sal_tag = job.find('span', class_="desktop")
                sal = sal_tag.text if sal_tag else None

                techstack = [skil.text for skil in skills] if skills else None

                location_tag = job.select_one("p.locations a")
                location = location_tag.get_text(strip=True) if location_tag else None

                jobPostedDate = dateFromtext(posted_time.lower()) if posted_time else None

                scrape_time = datetime.now().strftime("%Y-%m-%d")

                jd = {
                        "job_title": jobb,
                        "company": comp,
                        "status": status,
                        "salary": sal,
                        "tech_stack": techstack,
                        "location": location,
                        "scrape_time": scrape_time,
                        "posted_date": jobPostedDate
                    }

                job_data.append(jd)
        return job_data

    except Exception as e:

        logging.Exception(f"Failed to extract data :{e}")
        return job_data


'''
1.select_one : is a css selector
2.we have to use np.nan instead of None if we want to actually insert null into the csv
3.(skills) : it is not a tuple, (skills,) : tuple with 1 element
4.cur.lastrowid : the id of the last row which it has inserted
'''