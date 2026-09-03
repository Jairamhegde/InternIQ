import logging
import psycopg2
from extract.fetcher import get_soup
from extract.extractor import scrape_data

from insertRawData.insertRawData import insertRawData
from insertCleanData.insertCleanData import manage_operation
from transform.transformData import loadData


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
    "https://internshala.com/jobs/big-data-jobs/"
]


def internshala(url_list):
    logging.info("Execution started...")

    for url in url_list:
        for page in range(1, 10):

            link = url if page == 1 else f"{url}page-{page}"
            try:
                soup     = get_soup(link)
                raw_data = scrape_data(soup)

                if not raw_data:
                    logging.info(f"No data found on page {page} — stopping pagination for {url}")
                    break

                logging.info(f"Scraped {len(raw_data)} jobs from {link}")

                insertRawData(raw_data)

                logging.info(f"Inserted {len(raw_data)} jobs into raw_data schema (PostgreSQL)")

            except Exception as e:
                logging.exception(f"Failed scraping page {page} of {url}:{e}")
    logging.info(f"Started inserting into into clean data")
    # Transform all raw data once scraping is complete
    
    data = loadData()
    manage_operation(data)

    logging.info("Processed data inserted into clean_data schema (PostgreSQL)")


if __name__ == '__main__':
    internshala(url_list=page_url)