
import requests

def __make_request(url: str, org_key: str, event_key: str) -> bytes:

    cookies = {
        "org_key": org_key,
        "event_key": event_key,
    }
    headers = {
        "User-Agent":
        "Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US; rv:1.9.0.7) Gecko/2009021910 Firefox/3.0.7",
    }

    response = requests.get(url, cookies=cookies, headers=headers)

    return response.content


def request_scout_radioz_match_scouting(org_key, event_key):
    url = "https://scoutradioz.com/reports/exportdata?type=matchscouting"

    return __make_request(url, org_key, event_key)


def download_scout_radioz_match_scouting(org_key, event_key, output_file):
    content = request_scout_radioz_match_scouting(org_key, event_key)

    # If the download is empty, this means that the event likely hasn't started yet, so 
    # we will fill in the important columns and add minimal mock data.
    if len(content) == 0:
        import pandas as pd
        good_df = pd.read_csv("data/2025nysu/match_scouting.csv")
        columns = list(good_df.keys())
        content = bytes(",".join(columns), "utf-8")


    with open(output_file, 'wb') as f:
        f.write(content)

    if org_key == "frc8749":
        import pandas as pd
        df = pd.read_csv(output_file)

        df.rename(
            inplace=True,
            columns={
                "teleCoralL1": "teleopCoralL1",
                "teleCoralL2": "teleopCoralL2",
                "teleCoralL3": "teleopCoralL3",
                "teleCoralL4": "teleopCoralL4",
                "teleAlgaeNet": "teleopAlgaeNet",
                "teleAlgaeProcessor": "teleopAlgaeProc",
                "autoAlgaeNet": "autoAlgaeNet",
                "autoAlgaeProcessor": "autoAlgaeProc",
                "endgameBarge": "bargeStatus",
            },
        )
        lookup = df[df["bargeStatus"] == "Hanging on Deep Cage"].index
        df.loc[lookup, "bargeStatus"] = "Deep Cage"

        lookup = df[df["bargeStatus"] == "Hanging on Shallow Cage"].index
        df.loc[lookup, "bargeStatus"] = "Shallow Cage"

        df.to_csv(output_file, index=False)



def request_scout_radioz_pit_scouting(org_key, event_key):
    url = "https://scoutradioz.com/reports/exportdata?type=pitscouting"

    return __make_request(url, org_key, event_key)


def download_scout_radioz_pit_scouting(org_key, event_key, output_file):
    content = request_scout_radioz_pit_scouting(org_key, event_key)

    with open(output_file, 'wb') as f:
        f.write(content)
