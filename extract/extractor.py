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

    if measure == "day" or measure == "days":
        date = (datetime.now() - timedelta(days=value)).strftime("%Y-%m-%d")
        return date

    if measure == "week" or measure == "weeks":
        date = (datetime.now() - timedelta(weeks=value)).strftime("%Y-%m-%d")
        return date

    return None


 
LOCATION_HINTS = re.compile(r"work from home|work from office|hybrid", re.IGNORECASE)
def find_location(job_card):
    map_icon = job_card.find('i', class_=re.compile(r"map-pin", re.IGNORECASE))
    if map_icon:
        container = map_icon.find_parent(class_=re.compile(r"row-1-item"))
        if container:
            text = container.get_text(" ", strip=True)
            if text:
                return text
 
    loc_tag = job_card.find('p', class_=re.compile(r"\blocations\b", re.IGNORECASE))
    if loc_tag and loc_tag.get_text(strip=True):
        return loc_tag.get_text(strip=True)
 
    loc_tag = job_card.find(class_=re.compile(r"location", re.IGNORECASE))
    if loc_tag and loc_tag.get_text(strip=True):
        return loc_tag.get_text(strip=True)
 
    text = job_card.get_text(" ", strip=True)
    match = LOCATION_HINTS.search(text)
    return match.group(0).strip() if match else None

SALARY_PATTERN = re.compile(
    r"(₹|rs\.?|inr)\s?[\d,]+(\s?-\s?[\d,]+)?\s?(/month|/week|lpa|per month)?"
    r"|unpaid|not disclosed|performance based",
    re.IGNORECASE,
)
def extract_sal(job_card):
    money_icon = job_card.find('i', class_=re.compile(r"money", re.IGNORECASE))
    if money_icon:
        container = money_icon.find_parent(class_=re.compile(r"row-1-item"))
        if container:
            sal_tag = container.find('span', class_=re.compile(r"^desktop$", re.IGNORECASE))
            if sal_tag and sal_tag.get_text(strip=True):
                return sal_tag.get_text(strip=True)
 
    sal_tag = job_card.find(class_=re.compile(r"stipend|salary", re.IGNORECASE))
    if sal_tag and sal_tag.get_text(strip=True):
        return sal_tag.get_text(strip=True)
 
    text = job_card.get_text(" ", strip=True)
    match = SALARY_PATTERN.search(text)
    return match.group(0).strip() if match else None


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

                sal = extract_sal(job)

                techstack = skills

                location = find_location(job)

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