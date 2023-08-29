"""Module to parse HTML page about UNSC resolution agendas
"""
from loguru import logger
from bs4 import BeautifulSoup
from urllib.parse import urlparse


def parse_agenda_overview_page(agenda_page: dict) -> dict:
    """Parses a single year's overview page

    Args:
        agenda_page (dict): dict containing the year and byte data of the agenda list

    Returns:
        dict: parsed agenda items sorted by resolution
    """
    agendas = {}
    soup = BeautifulSoup(agenda_page["Data"], 'html5lib')
    table_rows = soup.find_all("tr")
    for row in table_rows:
        td_elements = row.find_all("td")
        
        if len(td_elements) == 0:
            continue
        links = td_elements[0].find_all("a", href=True)
        
        if "/en/" in links[len(links) -1]['href']:
            split_by = '.org/en/'
        else:
            split_by = '.org/'
        resolution_name = links[len(links) -1]['href'].split(split_by)[1].replace(" ", "").replace("%20", "")
        
        if len(resolution_name) < 11:
            resolution_name = f"{resolution_name}({agenda_page['Year']})"
        agenda = td_elements[len(td_elements) - 1].get_text()
        logger.debug(f"Parsed resolution {resolution_name} with agenda: {agenda}")
        agendas[resolution_name] = agenda
    return agendas

def parse_list_of_agenda_pages(agenda_pages: list[dict]) -> dict:
    """Parses a list of agenda pages each containing a single year of UNSC resolutions.

    Args:
        agenda_pages (list[dict]): list of dicts, each dict containing the year and byte data

    Returns:
        dict: dict of all parsed agendas sorted by resolutions
    """
    all_agendas = {}

    for i, page in enumerate(agenda_pages):
        logger.info(f"Parsing agenda page {i + 1} of {len(agenda_pages)} - year {page['Year']}")
        parsed_agendas = parse_agenda_overview_page(page)
        all_agendas = all_agendas | parsed_agendas
    
    logger.info(f"Parsed data for {len(all_agendas.keys())} resolutions.")
    
    return all_agendas