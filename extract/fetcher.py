import requests
from bs4 import BeautifulSoup
import logging

def get_soup(url):
        try:
                headers={"User-Agent":"Mozilla/5.0"}
                response=requests.get(url, headers=headers)
                response.raise_for_status()
                html = response.text
                return BeautifulSoup(html, "html.parser")
        except Exception as e:
                logging.error(f"Failed to fetch URL {url}: {e}")
                return None


