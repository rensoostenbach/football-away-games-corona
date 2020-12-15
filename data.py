import http.client
import json
import os
import pandas as pd
import time
import numpy as np

API_SOCCER = os.environ.get("API_SOCCER")
connection = http.client.HTTPConnection("api.football-data.org")
headers = {"X-Auth-Token": API_SOCCER}

# Eredivisie, Premier League, Bundesliga, Ligue 1, Serie A, Primera Divison
competitions = ["DED", "PL", "BL1", "FL1", "SA", "PD"]
seasons = [2018, 2019, 2020]

# Retrieving the data
for comp in competitions:
    for season in seasons:
        connection.request(
            "GET",
            f"/v2/competitions/{comp}/matches?season={season}&status=FINISHED",
            None,
            headers,
        )
        response = json.loads(connection.getresponse().read().decode())

        # Creating the empty DataFrame
        matches = pd.DataFrame()

        # Appending every match the the newly created DataFrame
        for match in response["matches"]:
            matches = matches.append(match, ignore_index=True)

        # Preprocessing
        # Correct type for ID and setting as index
        matches["id"] = matches["id"].astype("int32")
        matches = matches.set_index("id")
        # Remove odds
        matches = matches.drop(columns=["odds"])
        # Include winner as separate column
        matches["winner"] = [d.get("winner") for d in matches.score]
        # Include home team and away team as separate column
        matches["homeTeamName"] = [d.get("name") for d in matches.homeTeam]
        matches["awayTeamName"] = [d.get("name") for d in matches.awayTeam]

        ## Saving the data
        matches.to_csv(f"data/{comp}_{season}.csv")
        matches.to_pickle(f"data/{comp}_{season}.pickle")

        # Sleep 10 seconds, because we only have 10 calls per minute
        time.sleep(10)

# Preprocessing 2018
# Eredivisie, Premier League, Bundesliga, Ligue 1, Serie A, Primera Divison
competitions = ["DED", "PL", "BL1", "FL1", "SA", "PD"]
seasons = [2018]

for comp in competitions:
    for season in seasons:
        df = pd.read_pickle(f"data/{comp}_{season}.pickle")
        df["corona"] = "pre"
        df.to_pickle(f"data/{comp}_{season}.pickle")

# Preprocessing 2019
# Eredivisie, Premier League, Bundesliga, Ligue 1, Serie A, Primera Divison
competitions = ["DED", "PL", "BL1", "FL1", "SA", "PD"]
seasons = [2019]

# Dates manually looked up on worldfootball.net

for comp in competitions:
    for season in seasons:
        df = pd.read_pickle(f"data/{comp}_{season}.pickle")
        df["utcDate"] = pd.to_datetime(df["utcDate"]).dt.tz_localize(None)
        if comp == "DED":
            df["corona"] = "pre"
            df.to_pickle(f"data/{comp}_{season}.pickle")
        elif comp == "PL":
            # 1st of March, last game with fans
            df["corona"] = np.where(
                df["utcDate"] <= pd.Timestamp("2020-03-01").floor("D"), "pre", "post"
            )
            df.to_pickle(f"data/{comp}_{season}.pickle")
        elif comp == "BL1":
            # 8th of March, last game with fans
            df["corona"] = np.where(
                df["utcDate"] <= pd.Timestamp("2020-03-08").floor("D"), "pre", "post"
            )
            df.to_pickle(f"data/{comp}_{season}.pickle")
        elif comp == "FL1":
            df["corona"] = "pre"
            df.to_pickle(f"data/{comp}_{season}.pickle")
        elif comp == "SA":
            # 1st of March, last game with fans
            df["corona"] = np.where(
                df["utcDate"] <= pd.Timestamp("2020-03-01").floor("D"), "pre", "post"
            )
            df.to_pickle(f"data/{comp}_{season}.pickle")
        elif comp == "PD":
            # 8th of March, last game with fans
            df["corona"] = np.where(
                df["utcDate"] <= pd.Timestamp("2020-03-08").floor("D"), "pre", "post"
            )
            df.to_pickle(f"data/{comp}_{season}.pickle")

# Preprocessing 2020
# Eredivisie, Premier League, Bundesliga, Ligue 1, Serie A, Primera Divison
competitions = ["DED", "PL", "BL1", "FL1", "SA", "PD"]
seasons = [2020]

for comp in competitions:
    for season in seasons:
        df = pd.read_pickle(f"data/{comp}_{season}.pickle")
        df["corona"] = "post"
        df.to_pickle(f"data/{comp}_{season}.pickle")

# Combining all datasets
# Eredivisie, Premier League, Bundesliga, Ligue 1, Serie A, Primera Divison
competitions = ["DED", "PL", "BL1", "FL1", "SA", "PD"]
seasons = [2018, 2019, 2020]

final_df = pd.DataFrame()

for comp in competitions:
    for season in seasons:
        df = pd.read_pickle(f"data/{comp}_{season}.pickle")
        df["utcDate"] = pd.to_datetime(df["utcDate"]).dt.tz_localize(None)
        df["league"] = comp
        df["year"] = season
        final_df = final_df.append(df)

final_df.to_pickle("data/all_data.pickle")
final_df.to_csv("data/all_data.csv")
