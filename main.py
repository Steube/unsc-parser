"""Starter package to scrape and parse UN Security Counsil data."""
import sys

import fetch_data
import export
import htmlparser
import xmlparser

from loguru import logger


def main():
    """Starter method to parse UNSC resolution data
    """
    logger.remove()
    logger.add(sys.stderr, level="INFO")
    logger.info("Starting up...")
    
    resolution_data = fetch_data.fetch_unsc_xml_data()
    resolution_result = xmlparser.handle_xml_records(resolution_data)
    logger.info(f"Fetched {len(resolution_result)} resolutions.")

    agenda_data = fetch_data.fetch_unsc_agenda_html_data()
    agenda_result = htmlparser.parse_list_of_agenda_pages(agenda_data)

    logger.info(f"Fetched {len(agenda_result)} agendas.")

    result = export.merge_resolution_data_with_agendas(agenda_result, resolution_result)
    export.save_dict_to_pd_excel(result, "voting.xlsx")


if __name__ == "__main__":
    main()
