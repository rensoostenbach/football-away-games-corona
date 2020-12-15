import dash
import dash_core_components as dcc
import dash_bootstrap_components as dbc
import dash_html_components as html
from dash.dependencies import Input, Output
import plotly.graph_objects as go
import pandas as pd
import numpy as np
from dash.exceptions import PreventUpdate
from functions import (
    fill_df_teams,
    read_data,
    update_axes,
    preprocess_avg_points,
    fill_points_df,
)

app = dash.Dash(__name__, external_stylesheets=[dbc.themes.LUX])
server = app.server

# TODO: Constants in a separete file perhaps

# the style arguments for the sidebar. We use position:fixed and a fixed width
SIDEBAR_STYLE = {
    "position": "fixed",
    "top": 0,
    "left": 0,
    "bottom": 0,
    "width": "16rem",
    "padding": "2rem 1rem",
    "background-color": "#f8f9fa",
}

# the styles for the main content position it to the right of the sidebar and
# add some padding.
CONTENT_STYLE = {
    "margin-left": "18rem",
    "margin-right": "2rem",
    "padding": "2rem 1rem",
}

# colors for graphs
COLORS = ["mediumseagreen", "indianred", "lightslategray"]

# reorderlist
REORDERLIST = ["HOME_TEAM", "AWAY_TEAM", "DRAW"]

sidebar = html.Div(
    [
        html.H2("Options", className="display-4", style={"font-size": "200%"}),
        html.Hr(),
        html.P("Choose different options in this sidebar", className="lead"),
        dbc.FormGroup(
            [
                dbc.Label("Pre/Post corona or separate seasons"),
                dbc.RadioItems(
                    id="prepost_or_year",
                    options=[
                        {"label": "Pre/Post corona", "value": "prepost"},
                        {"label": "Separate seasons", "value": "year"},
                    ],
                    value="prepost",
                    custom=False,
                    style={"display": "block"},
                ),
            ]
        ),
        dbc.FormGroup(
            [
                dbc.Label("League selection"),
                dbc.RadioItems(
                    id="leagueselector",
                    options=[
                        {"label": "Premier League", "value": "PL"},
                        {"label": "Bundesliga", "value": "BL1"},
                        {"label": "Eredivisie", "value": "DED"},
                        {"label": "Serie A", "value": "SA"},
                        {"label": "Ligue 1", "value": "FL1"},
                    ],
                    value="PL",
                    custom=False,
                ),
            ]
        ),
        html.Div(
            dbc.FormGroup(
                [
                    # TODO: Think of a way how to combine different seasons/leagues
                    dbc.Label("Year selection"),
                    dbc.RadioItems(
                        id="yearselector",
                        options=[
                            {"label": "2018-2019", "value": "2018"},
                            {"label": "2019-2020", "value": "2019"},
                            {"label": "2020-2021", "value": "2020"},
                        ],
                        value="2020",
                        custom=False,
                    ),
                ]
            ),
            id="yeardiv",
        ),
        dbc.FormGroup(
            [
                # TODO: Preprocess the pre and post corona datasets, and think of a way how to combine different seasons/leagues
                html.Label(
                    "Pick a team to see the amount of home/away wins and draws they have."
                ),
                dcc.Dropdown(id="teamselector"),
            ]
        ),
    ],
    style=SIDEBAR_STYLE,
)

content = html.Div(
    [
        html.Div(
            children=[
                html.H1(
                    children="Football with and without fans",
                    style={
                        "textAlign": "center",
                    },
                ),
                html.P(
                    "This web app will show visualisations of how football has changed (or not) "
                    "due to the lack of fans in stadiums.",
                    style={
                        "textAlign": "center",
                    },
                ),
                html.Hr(),
            ]
        ),
        html.Div(
            [
                dcc.Markdown(id="single_winner_text", style={"text-align": "center"}),
                dcc.Graph(
                    id="single_winner_graph",
                ),
            ],
            id="single_winner_div",
        ),
        html.Div(
            [
                dcc.Markdown(id="double_winner_text", style={"text-align": "center"}),
                dcc.Graph(
                    id="double_winner_graph_pre",
                    style={"display": "inline-block", "width": "49%"},
                ),
                dcc.Graph(
                    id="double_winner_graph_post",
                    style={"display": "inline-block", "width": "49%"},
                ),
            ],
            id="double_winner_div",
        ),
        html.Div(
            [
                dcc.Markdown(id="avg_points_text", style={"text-align": "center"}),
                dcc.Graph(
                    id="avg_points_graph",
                ),
            ],
            id="avg_points_div",
        ),
        html.Div(
            [
                dcc.Markdown(
                    id="single_teamwinner_text", style={"text-align": "center"}
                ),
                dcc.Graph(
                    id="single_teamwinner_graph",
                ),
            ],
            id="single_teamwinner_div",
        ),
        html.Div(
            [
                dcc.Markdown(
                    id="double_teamwinner_text", style={"text-align": "center"}
                ),
                dcc.Graph(
                    id="double_teamwinner_graph_pre",
                    style={"display": "inline-block", "width": "49%"},
                ),
                dcc.Graph(
                    id="double_teamwinner_graph_post",
                    style={"display": "inline-block", "width": "49%"},
                ),
            ],
            id="double_teamwinner_div",
        ),
    ],
    id="page-content",
    style=CONTENT_STYLE,
)

app.layout = html.Div([sidebar, content])


@app.callback(Output("yeardiv", "style"), [Input("prepost_or_year", "value")])
def toggle_prepost_year(prepost_or_year):
    if prepost_or_year == "prepost":
        return {"display": "none"}
    elif prepost_or_year == "year":
        return {"display": "block"}


@app.callback(
    Output("teamselector", "options"),
    [
        Input("prepost_or_year", "value"),
        Input("leagueselector", "value"),
        Input("yearselector", "value"),
    ],
)
def set_teamselector_options(prepost_or_year, league, year):
    if prepost_or_year == "prepost":
        df_pre, df_post = read_data(prepost_or_year, league, year)
        df = pd.concat([df_pre, df_post])
    elif prepost_or_year == "year":
        df = read_data(prepost_or_year, league, year)

    return [
        {"label": team, "value": team} for team in np.sort(df["homeTeamName"].unique())
    ]


@app.callback(
    Output("single_winner_div", "style"),
    Output("double_winner_div", "style"),
    [Input("prepost_or_year", "value")],
)
def update_winner_styles(prepost_or_year):
    if prepost_or_year == "prepost":
        style_double_winner_div = {"display": "block"}
        style_single_winner_div = {"display": "none"}
        return style_single_winner_div, style_double_winner_div
    elif prepost_or_year == "year":
        style_single_winner_div = {"display": "block"}
        style_double_winner_div = {"display": "none"}
        return style_single_winner_div, style_double_winner_div


@app.callback(Output("avg_points_div", "style"), [Input("prepost_or_year", "value")])
def update_avg_points_style(prepost_or_year):
    if prepost_or_year == "prepost":
        return {"display": "block"}
    elif prepost_or_year == "year":
        return {"display": "none"}


@app.callback(
    Output("single_teamwinner_div", "style"),
    Output("double_teamwinner_div", "style"),
    [
        Input("prepost_or_year", "value"),
        Input("leagueselector", "value"),
        Input("teamselector", "value"),
        Input("yearselector", "value"),
    ],
)
def update_teamwinner_styles(prepost_or_year, league, teamname, year):
    if not teamname:
        return {"display": "none"}, {"display": "none"}

    if prepost_or_year == "prepost":
        # Below 5 lines are for making the team graph disappear when changing leagues
        df_pre, df_post = read_data(prepost_or_year, league, year)
        df = pd.concat([df_pre, df_post])
        all_teams = np.sort(
            df["homeTeamName"].unique()
        )  # Assuming all teams have played home at least once
        if teamname not in all_teams:
            return {"display": "none"}, {"display": "none"}

        style_double_teamwinner_div = {"display": "block"}
        style_single_teamwinner_div = {"display": "none"}
        return style_single_teamwinner_div, style_double_teamwinner_div
    elif prepost_or_year == "year":
        # Below 5 lines are for making the team graph disappear when changing leagues
        df = read_data(prepost_or_year, league, year)
        all_teams = np.sort(
            df["homeTeamName"].unique()
        )  # Assuming all teams have played home at least once
        if teamname not in all_teams:
            return {"display": "none"}, {"display": "none"}

        style_single_teamwinner_div = {"display": "block"}
        style_double_teamwinner_div = {"display": "none"}
        return style_single_teamwinner_div, style_double_teamwinner_div


@app.callback(
    Output("single_winner_graph", "figure"),
    Output("single_winner_text", "children"),
    [
        Input("prepost_or_year", "value"),
        Input("leagueselector", "value"),
        Input("yearselector", "value"),
    ],
)
def update_single_winner_graph(prepost_or_year, league, year):
    if prepost_or_year == "prepost":
        raise PreventUpdate

    df = read_data(prepost_or_year, league, year)
    df_winner = (
        df["winner"]
        .value_counts()
        .reindex(REORDERLIST)
        .rename_axis("Winning team")
        .reset_index(name="Counts")
    )
    fig = go.Figure(
        data=[
            go.Bar(
                x=df_winner["Winning team"], y=df_winner["Counts"], marker_color=COLORS
            )
        ]
    )

    update_axes(fig)

    winner_text = f"## Total number of home wins, draws and away wins in the {league}"

    return fig, winner_text


@app.callback(
    Output("double_winner_graph_pre", "figure"),
    Output("double_winner_graph_post", "figure"),
    Output("double_winner_text", "children"),
    [
        Input("prepost_or_year", "value"),
        Input("leagueselector", "value"),
        Input("yearselector", "value"),
    ],
)
def update_double_winner_graph(prepost_or_year, league, year):
    if prepost_or_year == "year":
        raise PreventUpdate

    df_pre, df_post = read_data(prepost_or_year, league, year)
    df_winner_pre = (
        df_pre["winner"]
        .value_counts()
        .reindex(REORDERLIST)
        .rename_axis("Winning team")
        .reset_index(name="Counts")
    )
    df_winner_post = (
        df_post["winner"]
        .value_counts()
        .reindex(REORDERLIST)
        .rename_axis("Winning team")
        .reset_index(name="Counts")
    )

    fig_pre = go.Figure(
        data=[
            go.Bar(
                x=df_winner_pre["Winning team"],
                y=df_winner_pre["Counts"],
                marker_color=COLORS,
            )
        ]
    )
    fig_post = go.Figure(
        data=[
            go.Bar(
                x=df_winner_post["Winning team"],
                y=df_winner_post["Counts"],
                marker_color=COLORS,
            )
        ]
    )

    update_axes(fig_pre)
    update_axes(fig_post)

    winner_text = f"## Total number of home wins, draws and away wins in the {league} before and after corona."

    return fig_pre, fig_post, winner_text


@app.callback(
    Output("avg_points_graph", "figure"),
    Output("avg_points_text", "children"),
    [
        Input("prepost_or_year", "value"),
        Input("leagueselector", "value"),
        Input("yearselector", "value"),
    ],
)
def update_avg_points_graph(prepost_or_year, league, year):
    if prepost_or_year == "year":
        raise PreventUpdate

    df_pre, df_post = read_data(prepost_or_year, league, year)
    df_pre = preprocess_avg_points(df_pre)
    df_post = preprocess_avg_points(df_post)

    # Fix for weird cases where matches from earlier match days were played in post corona time
    df_post = df_post[~df_post["yearMatchday"].isin(df_pre["yearMatchday"].unique())]

    points_df_pre = pd.DataFrame(
        0,
        index=df_pre["yearMatchday"].unique(),
        columns=["homeTeamPoints", "awayTeamPoints", "numberOfMatches"],
    )
    points_df_post = pd.DataFrame(
        0,
        index=df_post["yearMatchday"].unique(),
        columns=["homeTeamPoints", "awayTeamPoints", "numberOfMatches"],
    )

    points_df_pre = fill_points_df(df_pre, points_df_pre)
    points_df_post = fill_points_df(df_post, points_df_post)

    trace1_1 = go.Scatter(
        x=points_df_pre.index,
        y=points_df_pre["homeAvgPoints"],
        mode="lines",
        name="Average home team points before corona",
        line=dict(color="mediumseagreen"),
    )
    trace1_2 = go.Scatter(
        x=points_df_pre.index,
        y=points_df_pre["awayAvgPoints"],
        mode="lines",
        name="Average away team points before corona",
        line=dict(color="indianred"),
    )
    trace1_3 = go.Scatter(
        x=points_df_post.index,
        y=points_df_post["homeAvgPoints"],
        mode="lines",
        name="Average home team points after corona",
        line=dict(color="seagreen"),
    )
    trace1_4 = go.Scatter(
        x=points_df_post.index,
        y=points_df_post["awayAvgPoints"],
        mode="lines",
        name="Average away team points after corona",
        line=dict(color="firebrick"),
    )

    trace2_1 = go.Scatter(
        x=points_df_pre.index,
        y=points_df_pre["maHomePoints"],
        mode="lines",
        name="Average home team points before corona",
        line=dict(color="mediumseagreen"),
        visible=False,
    )
    trace2_2 = go.Scatter(
        x=points_df_pre.index,
        y=points_df_pre["maAwayPoints"],
        mode="lines",
        name="Average away team points before corona",
        line=dict(color="indianred"),
        visible=False,
    )
    trace2_3 = go.Scatter(
        x=points_df_post.index,
        y=points_df_post["maHomePoints"],
        mode="lines",
        name="Average home team points after corona",
        line=dict(color="seagreen"),
        visible=False,
    )
    trace2_4 = go.Scatter(
        x=points_df_post.index,
        y=points_df_post["maAwayPoints"],
        mode="lines",
        name="Average away team points after corona",
        line=dict(color="firebrick"),
        visible=False,
    )

    data = [
        trace1_1,
        trace1_2,
        trace1_3,
        trace1_4,
        trace2_1,
        trace2_2,
        trace2_3,
        trace2_4,
    ]

    updatemenus = list(
        [
            dict(
                active=0,
                showactive=True,
                x=0.57,
                y=1.2,
                buttons=list(
                    [
                        dict(
                            label="Average per matchday",
                            method="update",
                            args=[
                                {
                                    "visible": [
                                        True,
                                        True,
                                        True,
                                        True,
                                        False,
                                        False,
                                        False,
                                        False,
                                    ]
                                }
                            ],
                        ),
                        dict(
                            label="Rolling average over 3 matchdays",
                            method="update",
                            args=[
                                {
                                    "visible": [
                                        False,
                                        False,
                                        False,
                                        False,
                                        True,
                                        True,
                                        True,
                                        True,
                                    ]
                                }
                            ],
                        ),
                    ]
                ),
            )
        ]
    )

    layout = dict(
        showlegend=True,
        xaxis=dict(title="Year and matchday"),
        yaxis=dict(title="Points"),
        updatemenus=updatemenus,
    )

    fig = dict(data=data, layout=layout)

    text = f"## Average points for home and away teams in the {league}"

    return fig, text


@app.callback(
    Output("single_teamwinner_graph", "figure"),
    Output("single_teamwinner_text", "children"),
    [
        Input("prepost_or_year", "value"),
        Input("leagueselector", "value"),
        Input("yearselector", "value"),
        Input("teamselector", "value"),
    ],
)
def update_single_teamwinner_graph(prepost_or_year, league, year, teamname):
    if prepost_or_year == "prepost":
        raise PreventUpdate
    elif prepost_or_year == "year":
        df = read_data(prepost_or_year, league, year)

    all_teams = np.sort(
        df["homeTeamName"].unique()
    )  # Assuming all teams have played home at least once

    if teamname not in all_teams:
        return {}, ""

    dff = df[["winner", "homeTeamName", "awayTeamName"]]
    df_teams = pd.DataFrame(
        0, index=["HOME_TEAM", "AWAY_TEAM", "DRAW"], columns=list(all_teams)
    )
    df_teams = fill_df_teams(dff, df_teams)

    teamwinner_graph = go.Figure(
        data=[
            go.Bar(
                x=df_teams[teamname].index,
                y=df_teams[teamname].tolist(),
                marker_color=COLORS,
            )
        ]
    )

    update_axes(teamwinner_graph)

    teamwinner_text = f"### Home wins, draws and away wins for {teamname}"

    return teamwinner_graph, teamwinner_text


@app.callback(
    Output("double_teamwinner_graph_pre", "figure"),
    Output("double_teamwinner_graph_post", "figure"),
    Output("double_teamwinner_text", "children"),
    [
        Input("prepost_or_year", "value"),
        Input("leagueselector", "value"),
        Input("yearselector", "value"),
        Input("teamselector", "value"),
    ],
)
def update_double_teamwinner_graph(prepost_or_year, league, year, teamname):
    if prepost_or_year == "year":
        raise PreventUpdate
    elif prepost_or_year == "prepost":
        df_pre, df_post = read_data(prepost_or_year, league, year)
        df = pd.concat([df_pre, df_post])

    all_teams = np.sort(
        df["homeTeamName"].unique()
    )  # Assuming all teams have played home at least once

    if teamname not in all_teams:
        return {}, {}, ""

    all_teams_pre = np.sort(df_pre["homeTeamName"].unique())
    dff_pre = df_pre[["winner", "homeTeamName", "awayTeamName"]]
    df_teams_pre = pd.DataFrame(
        0, index=["HOME_TEAM", "AWAY_TEAM", "DRAW"], columns=list(all_teams_pre)
    )
    df_teams_pre = fill_df_teams(dff_pre, df_teams_pre)

    teamwinner_graph_pre = go.Figure(
        data=[
            go.Bar(
                x=df_teams_pre[teamname].index,
                y=df_teams_pre[teamname].tolist(),
                marker_color=COLORS,
            )
        ]
    )

    update_axes(teamwinner_graph_pre)

    all_teams_post = np.sort(df_post["homeTeamName"].unique())
    dff_post = df_post[["winner", "homeTeamName", "awayTeamName"]]
    df_teams_post = pd.DataFrame(
        0, index=["HOME_TEAM", "AWAY_TEAM", "DRAW"], columns=list(all_teams_post)
    )
    df_teams_post = fill_df_teams(dff_post, df_teams_post)

    teamwinner_graph_post = go.Figure(
        data=[
            go.Bar(
                x=df_teams_post[teamname].index,
                y=df_teams_post[teamname].tolist(),
                marker_color=COLORS,
            )
        ]
    )

    update_axes(teamwinner_graph_post)

    double_teamwinner_text = f"### Home wins, draws and away wins for {teamname}"

    return teamwinner_graph_pre, teamwinner_graph_post, double_teamwinner_text


if __name__ == "__main__":
    app.run_server(debug=True)
