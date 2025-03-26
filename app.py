
import dash
from dash import dcc, html, Input, Output, dash_table
import dash_bootstrap_components as dbc
import pandas as pd
import plotly.express as px
import numpy as np
import os


df = pd.read_csv('scrubbed.csv', low_memory=False)

df['datetime'] = pd.to_datetime(df['datetime'], errors='coerce')
df['year'] = df['datetime'].dt.year
df['year'] = df['year'].astype('Int64')
df.columns = df.columns.str.strip()

df['latitude'] = pd.to_numeric(df['latitude'], errors='coerce')
df['longitude'] = pd.to_numeric(df['longitude'], errors='coerce')
df.dropna(subset=['latitude', 'longitude'], inplace=True)

df['duration (seconds)'] = pd.to_numeric(df['duration (seconds)'], errors='coerce')

app = dash.Dash(__name__, external_stylesheets=[dbc.themes.LUX])

app.layout = dbc.Container([
    dbc.Navbar(
        dbc.Container([
            html.Div([
                html.H3("UFO Sightings Explorer", className="mb-0 text-white"),
                html.P("Visualize global UFO sightings with filters for year, country, shape, and duration.",
                       className="mb-0 text-white-50", style={"fontSize": "0.9rem"})
            ])
        ]),
        color="dark", dark=True, className="mb-4"
    ),

    dbc.Row([
        dbc.Col([
            html.H5("Filters", className="mb-2"),

            dbc.Label("Country"),
            dcc.Dropdown(
                options=[{"label": c.upper(), "value": c} for c in sorted(df['country'].dropna().unique())],
                id='country-filter', multi=True
            ),

            dbc.Label("Shape", className="mt-3"),
            dcc.Dropdown(
                options=[{"label": s.title(), "value": s} for s in sorted(df['shape'].dropna().unique())],
                id='shape-filter', multi=True
            ),

            dbc.Label("Year Range", className="mt-3"),
            dbc.Row([
                dbc.Col(dcc.Dropdown(
                    id='start-year-dropdown',
                    options=[{"label": str(y), "value": y} for y in sorted(df['year'].dropna().unique())],
                    placeholder="Start year",
                    clearable=True
                )),
                dbc.Col(dcc.Dropdown(
                    id='end-year-dropdown',
                    options=[{"label": str(y), "value": y} for y in sorted(df['year'].dropna().unique())],
                    placeholder="End year",
                    clearable=True
                ))
            ]),

            dbc.Label("Duration (seconds)", className="mt-3"),
            dcc.RangeSlider(
                id='duration-slider',
                min=0,
                max=1000,
                value=[0, 600],
                marks={
                    0: "0s", 60: "1m", 300: "5m", 600: "10m", 900: "15m", 1000: "Max"
                },
                step=1,
                tooltip={"placement": "bottom", "always_visible": False}
            )
        ], width=3),

        dbc.Col([
            html.Div(id='sightings-counter', className="text-end text-muted mb-2", style={"fontSize": "0.9rem"}),
            dcc.Loading(
                type="circle",
                children=[
                    dcc.Graph(id='ufo-map')
                ]
            )
        ], width=9)
    ]),
    dbc.Row([
        dbc.Col(
            html.Footer("Datasource: National UFO Reporting Center (NUFORC)",
                        className="text-center text-muted my-4"),
            width=12
        )
    ])
], fluid=True)

@app.callback(
    [Output('ufo-map', 'figure'),
     Output('sightings-counter', 'children')],
    [Input('country-filter', 'value'),
     Input('shape-filter', 'value'),
     Input('start-year-dropdown', 'value'),
     Input('end-year-dropdown', 'value'),
     Input('duration-slider', 'value')]
)
def update_map(countries, shapes, start_year, end_year, duration_range):
    dff = df.copy()
    if countries:
        dff = dff[dff['country'].isin(countries)]
    if shapes:
        dff = dff[dff['shape'].isin(shapes)]
    if start_year and end_year:
        dff = dff[(dff['year'] >= start_year) & (dff['year'] <= end_year)]
    dff = dff[(dff['duration (seconds)'] >= duration_range[0]) & (dff['duration (seconds)'] <= duration_range[1])]

    fig = px.scatter_map(
        dff,
        lat="latitude",
        lon="longitude",
        hover_name="city",
        hover_data={"datetime": True, "shape": True},
        color_discrete_sequence=["#1976D2"],
        zoom=1,
        height=600
    )

    counter_text = f"Total sightings: {len(dff):,}"
    return fig, counter_text

port = int(os.environ.get("PORT", 8051))

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=port)




