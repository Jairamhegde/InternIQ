import logging

from extract.fetcher import get_soup
from extract.extractor import scrape_data

from rawData.raw_data import insertRawData
from db.db_manager import manage_operation
from transform.transformData import loadData
# future imports
# from extract.cleanData import loadData
# from insights.insight import generate_insights


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

logging.info("Execution started...")


def internshala(url):

    for page in range(1, 21):

        if page == 1:
            link = url
        else:
            link = f"{url}page-{page}"

        try:

            soup = get_soup(link)

            raw_data = scrape_data(soup)

            logging.info(f"Scraped data from page {page}")

            insertRawData(raw_data)

            logging.info("Inserted raw data into rawData.db")

        except Exception:

            logging.exception(
                f"Failed scraping page {page}"
            )

    # Transform ALL raw data once
    data = loadData()
    manage_operation(data)

    logging.info(
        "Inserted processed data into jobs.db"
    )


if __name__ == '__main__':

    internshala(
        "https://internshala.com/jobs/"
        "net-development,"
        "ai-agent-development,"
        "asp-net,"
        "android-app-development,"
        "angular-js-development,"
        "backend-development,"
        "cloud-computing,"
        "cyber-security,"
        "front-end-development,"
        "full-stack-development,"
        "game-development,"
        "java,"
        "javascript-development,"
        "machine-learning,"
        "node-js-development,"
        "python-django,"
        "web-development-jobs/"
    )