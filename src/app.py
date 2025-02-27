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
    df['state'].dropna(inplace=True)
    df['Date'] = pd.to_datetime(df['Date'])

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

    # ship_states = set(df['state'].unique())
    # india_states = set(india['state'].unique())
    # missing_in_india = ship_states - india_states
    # missing_in_ship = india_states - ship_states

    # print("States in df but not in india:", missing_in_india)
    # print("States in india but not in df:", missing_in_ship)

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
state_sales = df.groupby('state')['Amount'].sum().reset_index()
map = (
    alt.Chart(india, width='container').mark_geoshape().encode(
        color=alt.Color("Amount:Q", legend=None),
        tooltip=['state:N', 'Amount:Q']
    ).transform_lookup(
        lookup="state",
        from_=alt.LookupData(state_sales, "state", ["Amount"])
    ).add_params(
        alt.selection_point(fields=["state"], name="selected_states")
    )
)
sales = alt.Chart(df, width='container').mark_line().encode(
            x=alt.X('yearmonth(Date):T', title='Month'),
            y=alt.Y('sum(Amount):Q', title='Total Amount')
        )

product_sales = df.groupby('Category')['Amount'].sum().reset_index()
product = alt.Chart(product_sales).mark_arc(innerRadius=50).encode(
            theta="Amount:Q",
            color=alt.Color("Category:N", legend=None)
        )

# Visuals
visuals = dbc.Row([
    dbc.Col(html.Div("Space for Filters"), md=4),
    dbc.Col([
        dbc.Row(dvc.Vega(id='map', spec=map.to_dict(format="vega"), signalsToObserve=['selected_states'])),
        dbc.Row([
            dbc.Col(dvc.Vega(id='sales', spec=sales.to_dict(format="vega"))),
            dbc.Col(dvc.Vega(id='product', spec=product.to_dict(format="vega")))
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
    Output("sales", "spec"),
    Input("map", "signalData"),
    prevent_initial_call=True
)
def sales_chart(signal_data):
    if not signal_data['selected_states']:
        # If no state selected, use the entire data set
        selection = df
    else:
        state = signal_data['selected_states']['state'][0]
        selection = df[df['state'] == state]

    sales = alt.Chart(selection, width='container').mark_line().encode(
                x=alt.X('yearmonth(Date):T', title='Month'),
                y=alt.Y('sum(Amount):Q', title='Total Amount')
            ).to_dict(format='vega')

    return sales

@callback(
    Output("product", "spec"),
    Input("map", "signalData"),
    prevent_initial_call=True
)
def product_chart(signal_data):
    if not signal_data['selected_states']:
        # If no state selected, use the entire data set
        selection = df.groupby('Category')['Amount'].sum().reset_index()
    else:
        state = signal_data['selected_states']['state'][0]
        selection = df[df['state'] == state].groupby('Category')['Amount'].sum().reset_index()
    
    product = alt.Chart(selection, width='container').mark_arc(innerRadius=50).encode(
                theta="Amount",
                color="Category:N",
            ).to_dict(format='vega')

    return product

# Run the app/dashboard
if __name__ == '__main__':
    app.run(debug=True)