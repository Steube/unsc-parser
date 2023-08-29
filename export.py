"""Module to export parsed UNSC resolution data to excel
"""
import pandas as pd
from loguru import logger
import openpyxl

def merge_resolution_data_with_agendas(agendas: dict, resolutions: list[dict]) -> list[dict]:
    """Merge data from a dict 

    Args:
        agendas (dict): _description_
        resolutions (list[dict]): _description_

    Returns:
        list[dict]: _description_
    """
    for resolution in resolutions:
        try:
            resolution["Agenda"] = agendas[resolution["Resolution"]]
        except KeyError:
            logger.warning(f"Agenda mismatch in resolution {resolution['Resolution']}, probably an off-by-one error.")
            resolution["Agenda"] = "Error in dataset."
    
    return resolutions

def save_dict_to_pd_excel(data: list[dict], filename: str):
    """Saves the dictionary via PD dataframe into an excel with the key as header and the value as row

    Args:
        data (dict): dict containing all values as a flat data structure
        filename (str): filename to save the excel as
    """
    # Putting the dictionary into the dataframe
    df = pd.DataFrame.from_dict(data)
    cols = ["Title", "Resolution", "Meeting Record", "Agenda", "Draft Resolution", "Vote Date", "Total Yes", "Total No", "Total Abstentions", "Total Non-Participating", "Total voting membership"]
    sorted_df = df[cols + [c for c in df.columns if c not in cols]]
    logger.info("Saving to Excel file...")
    # Writing the dataframe into an excel file
    try:
        sorted_df.to_excel(filename, index=None)
    except:
        logger.exception("Error saving xlsx. Permission error might occur if file is open in Excel.")
        