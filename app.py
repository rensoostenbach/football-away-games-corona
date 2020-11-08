# -*- coding: utf-8 -*-

# Run this app with `python app.py` and
# visit http://127.0.0.1:8050/ in your web browser.

import dash
import dash_core_components as dcc
import dash_html_components as html
import plotly.express as px
import pandas as pd

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

colors = {
    'background': '#111111',
    'text': '#7FDBFF'
}

# assume you have a "long-form" data frame
# see https://plotly.com/python/px-arguments/ for more options
df = pd.read_pickle('data\DED_2020.pickle')

df_winner = df['winner'].value_counts().rename_axis('Team').reset_index(name='Counts')

fig = px.bar(df_winner, x="Team", y="Counts", barmode="group")

fig.update_layout(
    plot_bgcolor=colors['background'],
    paper_bgcolor=colors['background'],
    font_color=colors['text']
)

app.layout = html.Div(style={'backgroundColor': colors['background']}, children=[
    html.H1(children='Football with and without fans', style={
        'textAlign': 'center',
        'color': colors['text']
    }
            ),

    html.Div(children='''
        This web app will show visualisations of how football has changed (or not) due to the lack of fans in stadiums.
    ''',  style={
        'textAlign': 'center',
        'color': colors['text']
    }
             ),

    dcc.Graph(
        id='example-graph',
        figure=fig
    )
])

if __name__ == '__main__':
    app.run_server(debug=True)
