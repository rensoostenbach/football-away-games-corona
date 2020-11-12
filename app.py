import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import plotly.express as px
import pandas as pd
import numpy as np
import os
from functions import fill_df_teams

API_SOCCER = os.environ.get("API_SOCCER")

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

server = app.server

app.layout = html.Div([
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

    html.Div([

        html.Label('League selection'),
        dcc.RadioItems(
            id='leagueselector',
            options=[
                {'label': 'Premier League', 'value': 'PL'},
                {'label': 'Bundesliga', 'value': 'BL1'},
                {'label': 'Eredivisie', 'value': 'DED'},
                {'label': 'Serie A', 'value': 'SA'},
                {'label': 'Ligue 1', 'value': 'FL1'}
            ],
            value='PL'
        )], style={'width': '15%', 'display': 'inline-block'}),

    html.Div([
        # TODO: Preprocess the pre and post corona datasets, and think of a way how to combine different seasons/leagues

        html.Label('Year selection'),
        dcc.RadioItems(
            id='yearselector',
            options=[
                {'label': '2018-2019', 'value': '2018'},
                {'label': '2019-2020', 'value': '2019'},
                {'label': '2020-2021', 'value': '2020'}
            ],
            value='2020'
        )], style={'width': '15%', 'display': 'inline-block'}),

    html.Div(
        dcc.Graph(
            id='winner_graph',
        )),

    html.Div([
        # TODO: Preprocess the pre and post corona datasets, and think of a way how to combine different seasons/leagues

        html.Label('Pick a team to see the amount of home/away wins and draws they have.'),
        dcc.Dropdown(
            id='teamselector'
        )], style={'width': '30%', 'display': 'inline-block'}),

    html.Div(
        dcc.Graph(
            id='teamwinner_graph',
        )
    )
])

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
