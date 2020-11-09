import http.client
import json
import os
import pandas as pd
import time
from apscheduler.schedulers.blocking import BlockingScheduler

API_SOCCER = os.environ.get("API_SOCCER")
connection = http.client.HTTPConnection('api.football-data.org')
headers = { 'X-Auth-Token': API_SOCCER }

# Eredivisie, Premier League, Bundesliga, Ligue 1, Serie A, Primera Divison
competitions = ['DED', 'PL', 'BL1', 'FL1', 'SA', 'PD']
seasons = [2018, 2019, 2020]

sched = BlockingScheduler()


@sched.scheduled_job('cron', day_of_week='tue', hour=12)
def scheduled_job():
    # Retrieving the data
    for comp in competitions:
        for season in seasons:
            connection.request('GET', f"/v2/competitions/{comp}/matches?season={season}&status=FINISHED", None, headers)
            response = json.loads(connection.getresponse().read().decode())

            # Creating the empty DataFrame
            matches = pd.DataFrame()

            # Appending every match the the newly created DataFrame
            for match in response['matches']:
                matches = matches.append(match, ignore_index=True)

            # Preprocessing
            # Correct type for ID and setting as index
            matches['id'] = matches['id'].astype('int32')
            matches = matches.set_index('id')
            # Remove odds
            matches = matches.drop(columns=['odds'])
            # Include winner as separate column
            matches['winner'] = [d.get('winner') for d in matches.score]
            # Include home team and away team as separate column
            matches['homeTeamName'] = [d.get('name') for d in matches.homeTeam]
            matches['awayTeamName'] = [d.get('name') for d in matches.awayTeam]

            ## Saving the data
            matches.to_csv(f"data/{comp}_{season}.csv")
            matches.to_pickle(f"data/{comp}_{season}.pickle")

            # Sleep 10 seconds, because we only have 10 calls per minute
            time.sleep(10)


sched.start()
