import json
from pathlib import Path
import pandas as pd
from typing import Dict, Any


############################################
# Statbotics Matches
############################################
def download_statbotics_matches(event: str, output_path: Path, quals_only=True):
    """
    Queries the statbotics api for event info, and saves the json file to disk.
    :param event: The event key (i.e. 2024paca)
    :param output_path: The path to save the json to
    :param quals_only: If true, only data from qualification matches will be saved
    """
    import statbotics

    sb = statbotics.Statbotics()

    elims = False if quals_only else None

    try:
        data = sb.get_matches(event=event, elims=elims)
        with open(output_path, "w") as f:
            json.dump(data, f, indent=4)
    except UserWarning:
        print("Could not load statbotics match data")



def load_statbotics_matches(filename: Path) -> pd.DataFrame:
    """
    Loads the match information from a file on disk, potentially pre-calculating helpful aggregate data
    :param filename: The filename to load
    :return: The data in the form of a dataframe
    """
    if not filename.exists():
        print("Statbotics match file does not exist!")
        return pd.DataFrame()
    with open(filename, "r") as f:
        json_data = json.load(f)

    return statbotics_matches_json_to_dataframe(json_data)


def statbotics_matches_json_to_dataframe(json_data: Dict[str, Any]) -> pd.DataFrame:
    """
    Converts the json data into a dataframe
    :param json_data: The json dictionary
    :return: The data frame
    """

    # There is nothing interesting to precalculate, so we just shove the json into a dataframe
    return pd.json_normalize(json_data)


############################################
# Statbotics Events
############################################
def download_statbotics_event_teams(event: str, output_path: Path):
    """
    Queries the API and downloads event data and saves the json response to disk.
    :param event: The event key (i.e. 2024paca)
    :param output_path: The location on disk to save the file
    """
    # import statbotics

    # sb = statbotics.Statbotics()
    # data = sb.get_event(event=event)
    #
    # with open(output_path, "w") as f:
    #     json.dump(data, f, indent=4)

    import requests

    url = f"https://api.statbotics.io/v3/team_events?event={event}"

    response = requests.get(url)

    with open(output_path, "w") as f:
        as_json = response.json()
        json.dump(as_json, f, indent=4)


def load_statbotics_teams(filename: Path):
    """
    Loads the json data for teams at an event from disk
    :param filename: The path to the cached json file.
    :return: The dataframe representing the json and some helpful precalculated aggregate data
    """
    with open(filename, "r") as f:
        json_data = json.load(f)

    return statbotics_teams_json_to_dataframe(json_data)


def statbotics_teams_json_to_dataframe(json_data: Dict[str, Any]) -> pd.DataFrame:
    """
    Converts teams into a dataframe, adding in some helpful precalculated aggregate data.
    :param json_data: The json dictionary
    :return: The data frame
    """
    output = pd.json_normalize(json_data)

    return output

