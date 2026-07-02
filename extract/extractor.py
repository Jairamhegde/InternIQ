from datetime import datetime, timedelta
import logging
import re
import pandas as pd
from keyword_match.text_tockenization import (generate_unigrams,
                                              generate_bigrams,
                                              get_matching_skills)


def dateFromtext(i):
    i = i.lower()

    if i in {"few hours ago","just now","today"}:
        return datetime.now().strftime("%Y-%m-%d")
    
    match = re.search(r'(\d+)\s+(hour|hours|day|days|week|weeks|month|months)\s+ago',i)
    if not match:
        return None

    value = int(match.group(1))
    measure = match.group(2)

    if measure in {"day","days"}:
        return (datetime.now() - timedelta(days=value)).strftime("%Y-%m-%d")
        
    if measure in {"week","weeks"}:
        return (datetime.now() - timedelta(weeks=value)).strftime("%Y-%m-%d")
        
    if measure in {"month","months"}:
        return (datetime.now() - timedelta(days= value* 30)).strftime("%Y-%m-%d")
    if measure in {"hour","hours"}:
        return  datetime.now().strftime("%Y-%m-%d")
    
def scrape_data(soup):

    job_data = []

    if soup is None:
        logging.error("scrape_data received no soup object")
        return job_data

    try:

        job_card = soup.find_all('div', class_="internship_meta experience_meta")
        if job_card:
            for job in job_card:
                postedtime_tag = job.select_one("div.color-labels  span")
                posted_time = postedtime_tag.text if postedtime_tag else None

                skills_tag = job.find_all("div", class_="job_skill")
                if skills_tag:
                    skills = [skill.get_text(strip = True)  for skill in skills_tag]
                else:
                    job_description = job.find("div", class_="text")

                    if job_description:

                        job_description = job_description.get_text(" ", strip=True)

                        unigrams = generate_unigrams(job_description)

                        bigrams = generate_bigrams(unigrams) if unigrams else set()

                        ngrams = set(unigrams) | bigrams

                        matched_skills = get_matching_skills(ngrams)

                        skills = matched_skills if matched_skills else None

                    else:
                        skills = None
                
    
                job_tag = job.find('a', id='job_title')
                jobb = job_tag.text if job_tag else None

                company_tag = job.find('p', class_="company-name")
                comp = company_tag.text if company_tag else None

                status_tag = job.find('div', class_="actively-hiring-badge")
                status = status_tag.text if status_tag else None


                money_icon = job.select_one("i.ic-16-money")
                sal = None
                if money_icon:
                    sal_tag = money_icon.find_next("span", class_= "desktop")
                    sal = sal_tag.get_text(strip = True) if sal_tag else None
                
                techstack = skills

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
                if not jd['job_title'] and  jd['company'] and jd['salary']:
                    continue
                else:
                    job_data.append(jd)
        return job_data

    except Exception as e:
        logging.exception(f"Failed to extract data :{e}")
        return job_data


'''
1.select_one : is a css selector
2.we have to use np.nan instead of None if we want to actually insert null into the csv
3.(skills) : it is not a tuple, (skills,) : tuple with 1 element
4.cur.lastrowid : the id of the last row which it has inserted
'''