"""Parse XML data from UNSC digital library MARCXML data.
"""
from operator import countOf
from lxml import etree
from loguru import logger

SUBFIELD_WITH_CODE = "{{*}}subfield[@code='{}']"
DATAFIELD_WITH_TAG = "{{*}}datafield[@tag='{}']"


def extract_voting_data(
    record: etree.Element, unanimous: bool, metadata: dict
) -> dict:
    """Extracts voting data and counts from a single resolution record

    Args:
        record (etree.Element): XML element containing a single resolution
        unanimous (bool): Whether the vote was unanimous, default False, used for recursion
        metadata (dict): Info about the resolution, for logging/debug purposes

    Returns:
        dict: voting data and counts
    """ 
    logger.debug(f"Extracting voting data for resolution {metadata['Resolution']}...")
    voting_data = {}
    for datafield in record.findall('.//{*}datafield[@tag="967"]'):
        country_code = datafield.find(SUBFIELD_WITH_CODE.format("c"))
        voting_result = datafield.find(SUBFIELD_WITH_CODE.format("d"))
        if not unanimous:
            if voting_result is None or len(voting_result.text) == 0:
                voting_data[country_code.text] = "NP"
            else:
                voting_data[country_code.text] = voting_result.text
        else:
            voting_data[country_code.text] = "Y"

    # Counting the total number of yes votes from the scraped data from "voting_data"
    voting_data["Total Yes"] = countOf(voting_data.values(), "Y")
    voting_data["Total No"] = countOf(voting_data.values(), "N")
    voting_data["Total Abstentions"] = countOf(voting_data.values(), "A")
    voting_data["Total Non-Participating"] = countOf(voting_data.values(), "NP")
    voting_data["Total voting membership"] = (
        voting_data["Total Yes"]
        + voting_data["Total No"]
        + voting_data["Total Abstentions"]
        + voting_data["Total Non-Participating"]
    )

    if not validate_voting_result(voting_data["Total Yes"], record):
        logger.warning(
            f"Discrepancy between calculated votes and XML data in {metadata['Resolution']}! Retrying with mitigation for unanimous votes..."
        )
        return extract_voting_data(record, True, metadata)

    if voting_data["Total Non-Participating"] == voting_data["Total voting membership"]:
        voting_data[
            "Note"
        ] = "In rare cases resolutions were adopted without a vote, showing all countries as non-voting."

    return voting_data


def validate_voting_result(yes_votes: int, record: etree.Element) -> bool:
    """Validates if the vote count is correct by comparing calculated number of yes votes to a value present in the dataset.

    Args:
        yes_votes (int): calculated number
        record (etree.Element): XML record of a resolution

    Returns:
        bool: True if it's a valid calculation
    """
    vote_counts = record.find(DATAFIELD_WITH_TAG.format("996"))
    comment = vote_counts.find(SUBFIELD_WITH_CODE.format("a"))
    yes_record = vote_counts.find(SUBFIELD_WITH_CODE.format("b"))

    # Unanimous votes contain comments or show all as non-participating
    if comment is not None:
        return True
    if yes_record is None:
        return True

    total_votes = int(yes_record.text)
    logger.debug(
        f"Total votes from XML: {total_votes}, total votes from calculated data: {yes_votes}"
    )
    return yes_votes == total_votes


def parse_metadata_from_record(record: etree.Element) -> dict:
    """Gets metadata from XML record

    Args:
        record (etree.Element): XML record of a resolution

    Returns:
        dict: dict containing title, resolution, meeting record, vote date and optionally draft resolution.
    """
    metadata = {}

    metadata["Title"] = (
        record.find(DATAFIELD_WITH_TAG.format("245"))
        .find(SUBFIELD_WITH_CODE.format("a"))
        .text
    )
    metadata["Resolution"] = (
        record.find(DATAFIELD_WITH_TAG.format("791"))
        .find(SUBFIELD_WITH_CODE.format("a"))
        .text
    )
    metadata["Meeting Record"] = (
        record.find(DATAFIELD_WITH_TAG.format("952"))
        .find(SUBFIELD_WITH_CODE.format("a"))
        .text
    )
    metadata["Vote Date"] = (
        record.find(DATAFIELD_WITH_TAG.format("269"))
        .find(SUBFIELD_WITH_CODE.format("a"))
        .text
    )
    try:
        metadata["Draft Resolution"] = (
            record.find(DATAFIELD_WITH_TAG.format("993"))
            .find(SUBFIELD_WITH_CODE.format("a"))
            .text
        )
    except AttributeError:
        logger.debug(f"Resolution {metadata['Resolution']} has no draft resolution.")

    return metadata


def handle_xml_records(xml_data: list[bytes]) -> list[dict]:
    """Iterates through a list of xml responses containing a year of resolutions, creating a dict containing vote data and metadata.

    Args:
        xml_data (list[bytes]): list of bytes, each byte set containing XML response data of one year

    Returns:
        _type_: dict containing metadata and vote data
    """
    result = []
    for i, year in enumerate(xml_data):
        logger.info(f"Parsing data record {i + 1} of {len(xml_data)}...")
        root = etree.fromstring(year)
        for record in root:
            title = (
                record.find(DATAFIELD_WITH_TAG.format("791"))
                .find(SUBFIELD_WITH_CODE.format("a"))
                .text
            )
            logger.debug(f"Parsing Resolution {title}...")
            metadata = parse_metadata_from_record(record)
            voting_data = extract_voting_data(record, False, metadata)
            logger.debug(f"Voting data: {voting_data}")
            logger.debug(f"Metadata: {metadata}")
            data = metadata | voting_data
            result.append(data)

    return result
