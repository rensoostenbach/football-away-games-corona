import dash
import dash_core_components as dcc
import dash_bootstrap_components as dbc
import dash_html_components as html
from dash.dependencies import Input, Output
import plotly.express as px
import pandas as pd
import numpy as np
import json
from functions import fill_df_teams, read_data

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
                    id='prepost_or_year',
                    options=[
                        {'label': 'Pre/Post corona', 'value': 'prepost'},
                        {'label': 'Separate seasons', 'value': 'year'}
                    ],
                    value='prepost',
                    custom=False,
                    style={'display': 'block'}
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
        html.Div(
            dbc.FormGroup(
                [
                    # TODO: Think of a way how to combine different seasons/leagues
                    dbc.Label('Pre / post corona'),
                    dbc.RadioItems(
                        id='prepostselector',
                        options=[
                            {'label': 'Pre corona', 'value': 'pre'},
                            {'label': 'Post corona', 'value': 'post'}
                        ],
                        value='pre',
                        custom=False
                    ),
                ]
            ), id='prepostdiv'),
        html.Div(
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
            ), id='yeardiv'),
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

        html.P('This web app will show visualisations of how football has changed (or not) '
               'due to the lack of fans in stadiums.', style={
            'textAlign': 'center',
        }
                 ),
        html.Hr()]),

    html.Div([dcc.Markdown(id='winner_text',
                          style={'text-align': 'center'}),
             dcc.Graph(
                 id='winner_graph',
             )]),

    html.Div([
        html.Div(
            dcc.Markdown(id='teamwinner_text',
                         style={'text-align': 'center'})
        ),
        html.Div(
            dcc.Graph(
                id='teamwinner_graph',
            )

        )
    ], id='teamwinnerdiv'

    )

], id="page-content", style=CONTENT_STYLE)

app.layout = html.Div([sidebar, content])


@app.callback(
    Output('prepostdiv', 'style'),
    Output('yeardiv', 'style'),
    [Input('prepost_or_year', 'value')])
def toggle_prepost_year(value):
    if value == 'prepost':
        return {'display': 'block'}, {'display': 'none'}
    elif value == 'year':
        return {'display': 'none'}, {'display': 'block'}


@app.callback(
    Output('teamselector', 'options'),
    [Input('leagueselector', 'value'),
     Input('yearselector', 'value')])
def set_teamselector_options(league, year):
    df = pd.read_pickle(f'data/{league}_{year}.pickle')
    return [{'label': team, 'value': team} for team in np.sort(df['homeTeamName'].unique())]


@app.callback(
    Output('winner_graph', 'figure'),
    Output('winner_text', 'children'),
    [Input('prepost_or_year', 'value'),
     Input('prepostselector', 'value'),
     Input('leagueselector', 'value'),
     Input('yearselector', 'value')])
def update_winner_graph(prepost_or_year, prepost, league, year):
    df = read_data(prepost_or_year, prepost, league, year)

    df_winner = df['winner'].value_counts().rename_axis('Team').reset_index(name='Counts')
    fig = px.bar(df_winner, x="Team", y="Counts", barmode="group")

    winner_text = f'## Total number of home wins, away wins and draws in the {league}'

    return fig, winner_text


@app.callback(
    Output('teamwinnerdiv', 'style'),
    [Input('teamselector', 'value')])
def update_teamwinner_div(value):
    if not value:
        return {'display': 'none'}
    else:
        return {'display': 'block'}


@app.callback(
    Output('teamwinner_graph', 'figure'),
    Output('teamwinner_text', 'children'),
    [Input('prepost_or_year', 'value'),
     Input('prepostselector', 'value'),
     Input('leagueselector', 'value'),
     Input('yearselector', 'value'),
     Input('teamselector', 'value')])
def update_teamwinner_graph(prepost_or_year, prepost, league, year, teamname):
    if not teamname:
        return {}, ''
    else:
        df = read_data(prepost_or_year, prepost, league, year)

        all_teams = np.sort(df['homeTeamName'].unique())  # Assuming all teams have played home at least once

        dff = df[['winner', 'homeTeamName', 'awayTeamName']]
        df_teams = pd.DataFrame(0, index=df['winner'].unique(), columns=all_teams)
        df_teams = fill_df_teams(dff, df_teams)

        teamwinner_graph = px.bar(df_teams, x=df_teams[teamname].index, y=df_teams[teamname].tolist(), barmode="group")
        teamwinner_graph.update_xaxes(title='Home/away win or draw')
        teamwinner_graph.update_yaxes(title=f'Amount of home/away wins or draw for {teamname}')

        teamwinner_text = f'### Home wins, away wins and draws for {teamname}'

        return teamwinner_graph, teamwinner_text


if __name__ == '__main__':
    app.run_server(debug=True)
