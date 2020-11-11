import dash
import dash_core_components as dcc
import dash_html_components as html
import plotly.express as px
import pandas as pd
import os

API_SOCCER = os.environ.get("API_SOCCER")

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

server = app.server

# assume you have a "long-form" data frame
# see https://plotly.com/python/px-arguments/ for more options
df = pd.read_pickle('data/DED_2020.pickle')

df_winner = df['winner'].value_counts().rename_axis('Team').reset_index(name='Counts')

fig = px.bar(df_winner, x="Team", y="Counts", barmode="group")

app.layout = html.Div(children=[
    html.H1(children='Football with and without fans', style={
        'textAlign': 'center',
    }
            ),

    html.Div(children='''
        This web app will show visualisations of how football has changed (or not) due to the lack of fans in stadiums.
    ''',  style={
        'textAlign': 'center',
    }
             ),

    dcc.Graph(
        id='example-graph',
        figure=fig
    )
])

if __name__ == '__main__':
    app.run_server(debug=True)
