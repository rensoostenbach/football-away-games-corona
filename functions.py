import pandas as pd
import plotly.graph_objects as go


def fill_df_teams(df, df_teams):
    for index, row in df.iterrows():
        if row[0] == "HOME_TEAM":
            df_teams[row[1]]["HOME_TEAM"] += 1
        elif row[0] == "AWAY_TEAM":
            df_teams[row[2]]["AWAY_TEAM"] += 1
        elif row[0] == "DRAW":
            df_teams[row[1]]["DRAW"] += 1
            df_teams[row[2]]["DRAW"] += 1

    return df_teams


def read_data(prepost_or_year, league, year):
    df = pd.read_pickle("data/all_data.pickle").dropna(subset=["matchday"])

    if prepost_or_year == "prepost":
        df_pre = df[(df["corona"] == "pre") & (df["league"] == league)]
        df_post = df[(df["corona"] == "post") & (df["league"] == league)]
        return df_pre, df_post
    elif prepost_or_year == "year":
        df = df[(df["year"] == int(year)) & (df["league"] == league)]
        return df


def update_axes(graph):
    graph.update_xaxes(title="Home/away win or draw")
    graph.update_yaxes(title=f"Amount")


def preprocess_avg_points(df):
    df = df.sort_values(by="utcDate")
    df["matchday"] = df["matchday"].astype(int)
    df["yearMatchday"] = df["year"].astype(str) + "_" + df["matchday"].astype(str)
    dff = df[["yearMatchday", "winner"]]
    return dff


def fill_points_df(df, points_df):
    for index, row in df.iterrows():
        points_df["numberOfMatches"][row[0]] += 1
        if row[1] == "HOME_TEAM":
            points_df["homeTeamPoints"][row[0]] += 3
        elif row[1] == "AWAY_TEAM":
            points_df["awayTeamPoints"][row[0]] += 3

    points_df["homeAvgPoints"] = (
        points_df["homeTeamPoints"] / points_df["numberOfMatches"]
    )
    points_df["awayAvgPoints"] = (
        points_df["awayTeamPoints"] / points_df["numberOfMatches"]
    )

    points_df["maHomePoints"] = points_df.iloc[:, 3].rolling(window=3).mean()
    points_df["maAwayPoints"] = points_df.iloc[:, 4].rolling(window=3).mean()

    return points_df
