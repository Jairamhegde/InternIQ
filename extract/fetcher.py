import requests
from bs4 import BeautifulSoup
import logging

def get_soup(url):
        try:
                headers={"User-Agent":"Mozilla/5.0"}
                response=requests.get(url,headers=headers)
                html=response.text
                soup=BeautifulSoup(html,"html.parser")
                return soup
        except Exception as e:
                logging.error(e)


