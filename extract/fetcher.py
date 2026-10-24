import asyncio
import html
import logging
import re
from datetime import datetime
from functools import lru_cache

import httpx
import requests
from bs4 import BeautifulSoup
from keyword_match.text_tokenization import (generate_unigrams,
                                             generate_bigrams,
                                             get_matching_skills)


def get_soup(url):
    try:
        headers = {"User-Agent": "Mozilla/5.0"}
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        html = response.text
        return BeautifulSoup(html, "html.parser")
    except Exception as e:
        logging.error(f"Failed to fetch URL {url}: {e}")
        return None


# ------------- PUBLIC JOB BOARD APIS (Greenhouse, Ashby) ------------------------
# Both APIs are public and need no API key. A company's board name is the last
# part of its careers URL, e.g. job-boards.greenhouse.io/databricks -> "databricks".

GREENHOUSE_URL = "https://boards-api.greenhouse.io/v1/boards/{board}/jobs"
ASHBY_URL = "https://api.ashbyhq.com/posting-api/job-board/{board}"

# board name -> company name. Only companies that list tech jobs in India.
GREENHOUSE_BOARDS = {
    "databricks": "Databricks",
    "okta": "Okta",
    "mongodb": "MongoDB",
    "gitlab": "GitLab",
    "rubrik": "Rubrik",
    "druva": "Druva",
    "stripe": "Stripe",
    "twilio": "Twilio",
    "coinbase": "Coinbase",
    "inmobi": "InMobi",
    "airbnb": "Airbnb",
    "razorpaysoftwareprivatelimited": "Razorpay",
}

ASHBY_BOARDS = {
    "sarvam": "Sarvam AI",
    "cursor": "Cursor",
    "openai": "OpenAI",
    "atlan": "Atlan",
    "composio": "Composio",
    "notion": "Notion",
}

# A job is "tech" when its title matches TECH_TITLE and not NON_TECH_TITLE.
TECH_TITLE = re.compile(
    r"engineer|developer|programmer|\bsde\b|software|data|machine learning|\bml\b|\bai\b|"
    r"devops|\bsre\b|reliability|cloud|backend|back end|frontend|front end|full.?stack|"
    r"android|\bios\b|mobile|security|\bqa\b|\btest|platform|infrastructure|architect|scientist",
    re.IGNORECASE,
)
NON_TECH_TITLE = re.compile(
    r"sales|account|marketing|recruit|talent|legal|counsel|finance|business development|"
    r"customer success|partnership|\bhr\b|people",
    re.IGNORECASE,
)

INDIA_LOCATION = re.compile(
    r"india|bengaluru|bangalore|mumbai|delhi|gurugram|gurgaon|noida|hyderabad|pune|"
    r"chennai|kolkata|ahmedabad|jaipur",
    re.IGNORECASE,
)

# Ashby currency code -> symbol that transform_data.detect_currency understands.
# Other currencies are skipped, because convert_to_inr would treat them as rupees.
CURRENCY_SYMBOL = {"INR": "₹", "USD": "$", "EUR": "€", "AED": "aed "}


def is_tech_job(title):
    return bool(TECH_TITLE.search(title)) and not NON_TECH_TITLE.search(title)


def skills_from_text(text):
    """Finds known skills in a job description, the same way extractor.py does."""
    unigrams = generate_unigrams(text)
    ngrams = set(unigrams) | generate_bigrams(unigrams)
    return get_matching_skills(ngrams)


def city_only(location):
    """'Bengaluru, Karnataka, India' -> 'Bengaluru'. insert_clean_data splits locations
    on commas, so the state and country would otherwise be stored as locations too."""
    if not location:
        return location
    return location.split(",")[0].strip()


def to_date(timestamp):
    """'2026-10-09T06:43:46-04:00' -> '2026-10-09'"""
    return timestamp[:10] if timestamp else None


def make_job(source, title, company, salary, skills, location, posted_date, job_link):
    """Builds a job in the same shape as extractor.scrape_data, so insert_raw_data can store it."""
    return {
        "job_title": title.strip(),
        "company": company,
        "status": None,
        "salary": salary,
        "tech_stack": skills or None,
        "location": location,
        "scrape_time": datetime.now().strftime("%Y-%m-%d"),
        "posted_date": posted_date,
        "job_link": job_link,
        "source": source,
    }


def greenhouse_to_job(job, company, india_only):
    title = job.get("title") or ""
    location = (job.get("location") or {}).get("name") or ""

    if not is_tech_job(title):
        return None
    if india_only and not INDIA_LOCATION.search(location):
        return None

    # content is HTML that has been escaped once more, e.g. "&lt;p&gt;"
    description_html = html.unescape(job.get("content") or "")
    description = BeautifulSoup(description_html, "html.parser").get_text(" ", strip=True)

    # Greenhouse has no salary field.
    return make_job(
        source="greenhouse",
        title=title,
        company=company,
        salary=None,
        skills=skills_from_text(description),
        location=city_only(location),
        posted_date=to_date(job.get("first_published") or job.get("updated_at")),
        job_link=job.get("absolute_url"),
    )


def ashby_salary(job):
    """Turns Ashby's salary component into text like '$211400 - 290600' that convert_salary can parse."""
    components = (job.get("compensation") or {}).get("summaryComponents") or []

    for part in components:
        if part.get("compensationType") != "Salary":
            continue

        symbol = CURRENCY_SYMBOL.get(part.get("currencyCode"))
        interval = part.get("interval")
        if not symbol or interval not in ("1 YEAR", "1 MONTH"):
            return None

        values = [int(v) for v in (part.get("minValue"), part.get("maxValue")) if v]
        if not values:
            return None

        salary = f"{symbol}{values[0]}" if len(values) == 1 else f"{symbol}{values[0]} - {values[1]}"
        if interval == "1 MONTH":
            salary += " /month"
        return salary

    return None


def ashby_location(job, india_only):
    """Returns the job's location, preferring an Indian one when the job lists several."""
    locations = [job.get("location") or ""]
    for extra in job.get("secondaryLocations") or []:
        locations.append(extra.get("location") or "")

    if not india_only:
        return locations[0]

    for location in locations:
        if INDIA_LOCATION.search(location):
            return location
    return None


def ashby_to_job(job, company, india_only):
    title = job.get("title") or ""

    if not job.get("isListed", True) or not is_tech_job(title):
        return None

    location = ashby_location(job, india_only)
    if india_only and not location:
        return None

    return make_job(
        source="ashby",
        title=title,
        company=company,
        salary=ashby_salary(job),
        skills=skills_from_text(job.get("descriptionPlain") or ""),
        location=city_only(location),
        posted_date=to_date(job.get("publishedAt")),
        job_link=job.get("jobUrl"),
    )


async def fetch_board(client, url, params, to_job, company, india_only):
    """Fetches one company's board and keeps its tech jobs. A failing board is logged and skipped."""
    try:
        response = await client.get(url, params=params)
        response.raise_for_status()
        jobs = response.json().get("jobs", [])
    except Exception as e:
        logging.error(f"Failed to fetch job board {url}: {e}")
        return []

    tech_jobs = []
    for job in jobs:
        parsed = to_job(job, company, india_only)
        if parsed:
            tech_jobs.append(parsed)

    logging.info(f"{company}: kept {len(tech_jobs)} tech jobs out of {len(jobs)}")
    return tech_jobs


async def fetch_api_jobs_async(india_only=True):
    requests_to_make = []
    for board, company in GREENHOUSE_BOARDS.items():
        url = GREENHOUSE_URL.format(board=board)
        requests_to_make.append((url, {"content": "true"}, greenhouse_to_job, company))
    for board, company in ASHBY_BOARDS.items():
        url = ASHBY_URL.format(board=board)
        requests_to_make.append((url, {"includeCompensation": "true"}, ashby_to_job, company))

    # All boards are fetched at the same time instead of one after another.
    async with httpx.AsyncClient(timeout=30, headers={"User-Agent": "Mozilla/5.0"}) as client:
        results = await asyncio.gather(*[
            fetch_board(client, url, params, to_job, company, india_only)
            for url, params, to_job, company in requests_to_make
        ])

    return [job for board_jobs in results for job in board_jobs]


@lru_cache(100)
def fetch_api_jobs(india_only=True):
    try:
        rsponse = asyncio.run(fetch_api_jobs_async(india_only))
    except Exception as e:
        return e
    return rsponse


if __name__ == "__main__":
    jobs = fetch_api_jobs()
    print(f"{len(jobs)} tech jobs")
    print(jobs[:3])
