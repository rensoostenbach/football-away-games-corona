import pandas as pd


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


def read_data(prepost_or_year, league, year):
    df = pd.read_pickle('data/all_data.pickle')

    if prepost_or_year == 'prepost':
        df_pre = df[(df['corona'] == 'pre') & (df['league'] == league)]
        df_post = df[(df['corona'] == 'post') & (df['league'] == league)]
        return df_pre, df_post
    elif prepost_or_year == 'year':
        df = df[(df['year'] == int(year)) & (df['league'] == league)]
        return df
