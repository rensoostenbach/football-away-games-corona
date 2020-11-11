import pandas as pd
import numpy as np


def fill_df_teams(df, df_teams):
    for index, row in df.iterrows():
        if row[0] == 'HOME_TEAM':
            df_teams[row[1]]['HOME_TEAM'] += 1
        elif row[0] == 'AWAY_TEAM':
            df_teams[row[2]]['AWAY_TEAM'] += 1
        elif row[0] == 'DRAW':
            df_teams[row[1]]['DRAW'] += 1
            df_teams[row[2]]['DRAW'] += 1

    return df_teams
