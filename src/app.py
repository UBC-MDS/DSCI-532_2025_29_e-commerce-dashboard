from dash import Dash, html, dcc, Input, Output, callback
import dash_bootstrap_components as dbc
import dash_vega_components as dvc
import pandas as pd
import altair as alt
import geopandas as gpd

alt.data_transformers.enable('vegafusion')

def import_data():
    df = pd.read_csv('data/raw/amazon_sample.zip')
    df = df.iloc[:, :-1]  # Drop last column
    df.rename(columns={'ship-state' : 'state'}, inplace=True)
    df['state'] = df['state'].str.title()

    india = gpd.read_file('data/states_india.geojson')
    india.drop(labels=['cartodb_id', 'state_code'], inplace=True, axis=1)
    india.rename(columns={'st_nm' : 'state'}, inplace=True)

    state_mapping = {
        'Dadra And Nagar': 'Dadara & Nagar Havelli',
        'Delhi': 'NCT of Delhi',
        'Arunachal Pradesh': 'Arunanchal Pradesh',
        'New Delhi': 'NCT of Delhi',
        'Andaman & Nicobar ': 'Andaman & Nicobar Island',
        'Rj': 'Rajasthan'  # Assuming 'Rj' stands for Rajasthan
    }

    # Rename values in df
    df['state'] = df['state'].replace(state_mapping)
    df.drop(df[df['state'] == 'Ladakh'].index, inplace=True)
    df.dropna(inplace=True)

    # ship_states = set(df['ship-state'].unique())
    # india_states = set(india['st_nm'].unique())
    # missing_in_india = ship_states - india_states
    # missing_in_ship = india_states - ship_states

    # print("States in df['ship-state'] but not in india['st_nm']:", missing_in_india)
    # print("States in india['st_nm'] but not in df['ship-state']:", missing_in_ship)

    return df, india

# Initiatlize the app
app = Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])
server = app.server

# Data
df, india = import_data()

# Components
# Header / Title
title = dbc.Row(html.H1("Sales Dashboard"))

# Metrics
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
map = (
    alt.Chart(india).mark_geoshape().encode(
    #   color=alt.Color('Amount:Q', aggregate='sum'),
    # ).transform_lookup(
    #     lookup="state",
    #     from_=alt.LookupData(df, "state", ["Amount"])
    ).add_params(
        alt.selection_point(fields=["state"], name="selected_states")
    )
)
chart1 = None # placeholder for chart 1
chart2 = None # placeholder for chart 2

# Visuals
visuals = dbc.Row([
    dbc.Col(html.Div("Space for Filters"), md=4),
    dbc.Col([
        dbc.Row(dcc.Graph(figure=map)),
        dbc.Row([
            dbc.Col(dvc.Vega(id='line', spec={})),
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
@callback(
    Output("line", "spec"),
    Input("map", "signalData")
)
def create_chart(signal_data):
    state = signal_data['selected_states']['state'][0]

    if not state:
        # Show all data if no states are selected
        return alt.Chart(df).mark_line().encode(
            x='Date',
            y='sum(Amount)'
        ).to_dict(format='vega')
    else:
        return alt.Chart(df[df['state'] == state]).mark_line().encode(
                x='Date',
                y='sum(Amount)'
        ).to_dict(format='vega')

# Run the app/dashboard
if __name__ == '__main__':
    app.run(debug=False)