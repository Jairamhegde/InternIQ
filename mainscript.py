import logging
from extract.fetcher import get_soup, fetch_api_jobs
from extract.extractor import scrape_data

from insert_raw_data.insert_raw_data import insert_raw_data
from insert_clean_data.insert_clean_data import manage_operation
from transform.transform_data import load_data


logging.basicConfig(
    level=logging.INFO,
    format=(
        "%(asctime)s | %(levelname)s | "
        "%(filename)s:%(lineno)d | "
        "%(funcName)s() | %(message)s"
    ),
    handlers=[
        logging.FileHandler("logfile.log"),
        logging.StreamHandler()
    ]
)

page_url = [
    "https://internshala.com/jobs/machine-learning-jobs/",
    "https://internshala.com/jobs/backend-development-jobs/",
    "https://internshala.com/fresher-jobs/front-end-development-jobs/",
    "https://internshala.com/jobs/mobile-app-development-jobs/",
    "https://internshala.com/jobs/big-data-jobs/",
    "https://internshala.com/jobs/ai-agent-development-jobs/",
    "https://internshala.com/jobs/angular-js-development-jobs/",
    "https://internshala.com/jobs/artificial-intelligence-ai-jobs/",
    "https://internshala.com/jobs/cloud-computing-jobs/",
    "https://internshala.com/jobs/engineering-jobs/"
]


def internshala(url_list):
    """Scrapes every Internshala category page and returns the jobs found."""
    jobs = []

    for url in url_list:
        for page in range(1, 10):

            link = url if page == 1 else f"{url}page-{page}"
            try:
                soup = get_soup(link)
                raw_data = scrape_data(soup)

                if not raw_data:
                    logging.info(f"No data found on page {page} — stopping pagination for {url}")
                    break

                logging.info(f"Scraped {len(raw_data)} jobs from {link}")
                jobs.extend(raw_data)

            except Exception as e:
                logging.exception(f"Failed scraping page {page} of {url}:{e}")

    return jobs


def run_pipeline():
    logging.info("Execution started...")

    jobs = internshala(page_url)

    try:
        api_jobs = fetch_api_jobs()
        logging.info(f"Fetched {len(api_jobs)} tech jobs from Greenhouse and Ashby")
        jobs.extend(api_jobs)
    except Exception:
        logging.exception("Failed to fetch jobs from Greenhouse and Ashby")

    try:
        insert_raw_data(jobs)
        logging.info(f"Inserted {len(jobs)} jobs into raw_data schema (PostgreSQL)")
    except Exception:
        logging.exception("Failed to insert into raw data.")
        return

    logging.info("Started inserting into clean data")
    try:
        data = load_data()
        manage_operation(data)
    except Exception as e:
        logging.exception("Failed to insert into clean data.")

    logging.info("Processed data inserted into clean_data schema (PostgreSQL)")


if __name__ == '__main__':
    run_pipeline()
