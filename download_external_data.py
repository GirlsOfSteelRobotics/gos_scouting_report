import pathlib

from metadata import SCOUT_RADIOZ_ORG, CURRENT_EVENT

from utils.scout_radioz_utils import (
    download_scout_radioz_match_scouting,
    download_scout_radioz_pit_scouting,
)
from utils.statbotics_utils import (
    download_statbotics_matches,
    download_statbotics_event_teams,
)
from utils.tba_utils import download_tba_event_matches


def download_external_data(event):
    """
    Downloads the external data (Statbotics, TBA, etc) for a specific event
    :param event: The event key
    """
    script_directory = pathlib.Path(__file__).resolve().parent

    data_directory = script_directory / "data" / event
    data_directory.mkdir(parents=True, exist_ok=True)

    download_statbotics_matches(event, data_directory / "statbotics_matches.json")
    download_statbotics_event_teams(event, data_directory / "statbotics_teams.json")
    download_tba_event_matches(event, data_directory / "tba_matches.json")

    download_scout_radioz_match_scouting(
        SCOUT_RADIOZ_ORG, event, data_directory / "match_scouting.csv"
    )
    download_scout_radioz_pit_scouting(
        SCOUT_RADIOZ_ORG, event, data_directory / "pit_scouting.csv"
    )


if __name__ == "__main__":
    download_external_data(CURRENT_EVENT)
