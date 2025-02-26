from dash import Dash, html, dcc, Input, Output, callback
import dash_bootstrap_components as dbc
import pandas as pd
import plotly.express as px
import json
import zipfile

# Initiatlize the app
app = Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])
server = app.server

# Unzip and import data
with zipfile.ZipFile('data/raw/amazon_sample.zip', 'r') as z:
    with z.open('amazon_sample.csv') as f:
        df = pd.read_csv(f)
df = df.iloc[:, :-1] # Drop last column
df['ship-state'] = df['ship-state'].str.title()

# Pre-aggregate data
sales = df.groupby('ship-state').agg('sum')['Amount'].reset_index()
sales.rename(columns={'ship-state':'State'}, inplace=True)

# Load map (need to replace this code to pull map data from naturalearthdata.com)
with open('data/states_india.geojson') as f:
    geojson = json.load(f)

# Plot choropleth map
fig = px.choropleth(sales, 
                    geojson=geojson, 
                    locations='State', 
                    featureidkey="properties.st_nm",
                    color='Amount',
                    color_continuous_scale="GnBu",
                    range_color=(100000, 1000000),
                    labels={'Amount':'Revenue'}
                   )
fig.update_geos(fitbounds="locations", visible=False)
fig.update_layout(margin={"r":0,"t":0,"l":0,"b":0})

# Components

# Header / Title
title = dbc.Row(html.H1("Sales Dashboard"))

#Metrics
metric_1 = dbc.Card(
    dbc.CardBody(
        [
            html.H3("Metric 1", 
                    className="card-title"
                    ),
            html.H1("$24,560", 
                    className="card-text"
                    ),
            html.Small("+20% month over month",
                       className="card-text text-muted"
                       )
        ]
    ),
    style={"width": "18rem"},
)

metric_2 = dbc.Card(
    dbc.CardBody(
        [
            html.H3("Metric 1", 
                    className="card-title"
                    ),
            html.H1("$24,560", 
                    className="card-text"
                    ),
            html.Small("+20% month over month",
                       className="card-text text-muted"
                       )
        ]
    ),
    style={"width": "18rem"},
)

metric_3 = dbc.Card(
    dbc.CardBody(
        [
            html.H3("Metric 1", 
                    className="card-title"
                    ),
            html.H1("$24,560", 
                    className="card-text"
                    ),
            html.Small("+20% month over month",
                       className="card-text text-muted"
                       )
        ]
    ),
    style={"width": "18rem"},
)

metrics = dbc.Row([
    dbc.Col(metric_1),
    dbc.Col(metric_2),
    dbc.Col(metric_3),
])

# Filters

filters = None # placeholder for filters

# Charts
chart1 = None # placeholder for chart 1
chart2 = None # placeholder for chart 2


# Visuals
visuals = dbc.Row([
    dbc.Col(html.Div("Space for Filters"), md=4),
    dbc.Col([
        dbc.Row(dcc.Graph(figure=fig)),
        dbc.Row([
            dbc.Col(html.Div("Chart 1 goes here")),
            dbc.Col(html.Div("Chart 2 goes here")),
            ]),
        ]),
])

# Layout
app.layout = dbc.Container([
    title,
    metrics,
    visuals
])


# Server side callbacks/reactivity
# ...

# Run the app/dashboard
if __name__ == '__main__':
    app.run(debug=False)