import dash
import dash_core_components as dcc
import dash_bootstrap_components as dbc
import dash_html_components as html
from dash.dependencies import Input, Output
import plotly.express as px
import pandas as pd
import numpy as np
import os
from functions import fill_df_teams

app = dash.Dash(__name__, external_stylesheets=[dbc.themes.LUX])

server = app.server

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

sidebar = html.Div(
    [
        html.H2("Options", className="display-4", style={'font-size': '200%'}),
        html.Hr(),
        html.P(
            "Choose different options in this sidebar", className="lead"
        ),
        dbc.FormGroup(
            [
                dbc.Label('Pre/Post corona or separate seasons'),
                dbc.RadioItems(
                    id='prepostcorona',
                    options=[
                        {'label': 'Pre/Post corona', 'value': 'prepost'},
                        {'label': 'Separate seasons', 'value': 'separate'}
                    ],
                    value='prepost',
                    custom=False
                ),
            ]
        ),
        dbc.FormGroup(
            [
                dbc.Label('League selection'),
                dbc.RadioItems(
                    id='leagueselector',
                    options=[
                        {'label': 'Premier League', 'value': 'PL'},
                        {'label': 'Bundesliga', 'value': 'BL1'},
                        {'label': 'Eredivisie', 'value': 'DED'},
                        {'label': 'Serie A', 'value': 'SA'},
                        {'label': 'Ligue 1', 'value': 'FL1'}
                    ],
                    value='PL',
                    custom=False

                ),
            ]
        ),
        dbc.FormGroup(
            [
                # TODO: Preprocess the pre and post corona datasets, and think of a way how to combine different seasons/leagues
                dbc.Label('Year selection'),
                dbc.RadioItems(
                    id='yearselector',
                    options=[
                        {'label': '2018-2019', 'value': '2018'},
                        {'label': '2019-2020', 'value': '2019'},
                        {'label': '2020-2021', 'value': '2020'}
                    ],
                    value='2020',
                    custom=False
                ),
            ]
        ),
        dbc.FormGroup(
            [
                # TODO: Preprocess the pre and post corona datasets, and think of a way how to combine different seasons/leagues
                html.Label('Pick a team to see the amount of home/away wins and draws they have.'),
                dcc.Dropdown(id='teamselector')
            ]
        )
    ],
    style=SIDEBAR_STYLE,
)

content = html.Div([
    html.Div(children=[
        html.H1(children='Football with and without fans', style={
            'textAlign': 'center',
        }
                ),

        html.Div(children='''
        This web app will show visualisations of how football has changed (or not) due to the lack of fans in stadiums.
    ''', style={
            'textAlign': 'center',
        }
                 )]),

    html.Div(
        dcc.Graph(
            id='winner_graph',
        )),

    html.Div(
        dcc.Graph(
            id='teamwinner_graph',
        )
    )
],id="page-content", style=CONTENT_STYLE)

app.layout = html.Div([sidebar, content])

@app.callback(
    Output(F)
)


@app.callback(
    Output('teamselector', 'options'),
    [Input('leagueselector', 'value'),
     Input('yearselector', 'value')]
)
def set_teamselector_options(league, year):
    df = pd.read_pickle(f'data/{league}_{year}.pickle')
    return [{'label': team, 'value': team} for team in np.sort(df['homeTeamName'].unique())]


@app.callback(
    Output('winner_graph', 'figure'),
    [Input('leagueselector', 'value'),
     Input('yearselector', 'value')]
)
def update_winner_graph(league, year):
    df = pd.read_pickle(f'data/{league}_{year}.pickle')

    df_winner = df['winner'].value_counts().rename_axis('Team').reset_index(name='Counts')
    fig = px.bar(df_winner, x="Team", y="Counts", barmode="group")

    return fig


@app.callback(
    Output('teamwinner_graph', 'figure'),
    [Input('leagueselector', 'value'),
     Input('yearselector', 'value'),
     Input('teamselector', 'value')]
)
def update_teamwinner_graph(league, year, teamname):
    df = pd.read_pickle(f'data/{league}_{year}.pickle')

    all_teams = np.sort(df['homeTeamName'].unique())  # Assuming all teams have played home at least once

    dff = df[['winner', 'homeTeamName', 'awayTeamName']]
    df_teams = pd.DataFrame(0, index=df['winner'].unique(), columns=all_teams)
    df_teams = fill_df_teams(dff, df_teams)

    teamwinner_graph = px.bar(df_teams, x=df_teams[teamname].index, y=df_teams[teamname].tolist(), barmode="group")
    teamwinner_graph.update_xaxes(title='Home/away win or draw')
    teamwinner_graph.update_yaxes(title='Amount of home/away wins or draw for selected team')
    return teamwinner_graph


if __name__ == '__main__':
    app.run_server(debug=True)
