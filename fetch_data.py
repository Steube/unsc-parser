"""Module to handle requests parsing UNSC resolution metadata and agendas
"""
import datetime
import time
import requests
from loguru import logger

RESOLUTION_URL =  "https://digitallibrary.un.org/search?ln=en&p=&f=&rm=&sf=&so=d&rg=200&c=Resource+Type&c=UN+Bodies&c=&of=xm&fti=0&fct__1=Voting+Data&fct__2=Security+Council&fct__3={}&fti=0"
AGENDA_URL = "https://www.un.org/securitycouncil/content/resolution{}-adopted-security-council-{}"
USER_AGENT = "User-Agent': 'Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Mobile Safari/537.36"

START_YEAR = 1946
CURRENT_YEAR = datetime.date.today().year

def fetch_unsc_xml_data() -> list[bytes]:
    """Fetches UNSC MARCXML data from UN's digital library

    Returns:
        list[bytes]: list of byte responses, each containing one year of resolutions.
    """
    data_elements = []

    for i in range(START_YEAR, CURRENT_YEAR + 1):
        logger.info(f"Fetching resolutions for {i}...")
        session = requests.Session()
        session.headers.update({'User-Agent': USER_AGENT})
        response = session.get(RESOLUTION_URL.format(i), timeout = 20)

        while (response.status_code != 200):
            logger.warning(f"Response: Status: {response.status_code}. Trying again...")
            time.sleep(5)
            response = session.get(RESOLUTION_URL.format(i), timeout = 20)
        data_elements.append(response.content) 
        logger.debug(f"Data length:{len(response.content)}")

    return data_elements



def fetch_unsc_agenda_html_data() -> list[dict]:
    """Fetches UNSC agenda HTML pages

    Returns:
        list[dict]: list of dicts containing the year and byte data of resolution agendas
    """
    agenda_data = []

    for i in range(START_YEAR, CURRENT_YEAR + 1):
        logger.info(f"Fetching agendas for {i}...")
        session = requests.Session()
        session.headers.update({'User-Agent': USER_AGENT})
        request_url = AGENDA_URL.format("s", i)
        response = session.get(request_url, timeout = 20)

        if (response.status_code == 404):
            logger.warning(f"Nonstandard URL for year {i}, probably needs a different request URL for page with single resolution.")
            request_url = AGENDA_URL.format("", i)
        
        while (response.status_code != 200):
            logger.warning(f"Response: Status: {response.status_code}. Trying again...")
            time.sleep(5)
            response = session.get(request_url, timeout = 20)
        agenda_data.append({"Year": i, "Data": response.content})
        logger.debug(f"Data length:{len(response.content)}")

    return agenda_data