from dash import Dash, html, dcc, Input, Output, callback
import dash_bootstrap_components as dbc
import dash_vega_components as dvc
import pandas as pd
import altair as alt
import geopandas as gpd
import plotly.express as px

alt.data_transformers.enable('vegafusion')

url = 'https://naciscdn.org/naturalearth/50m/cultural/ne_50m_admin_1_states_provinces.zip'
world_regions = gpd.read_file(url)[['wikipedia', 'name', 'admin', 'postal', 'latitude', 'longitude', 'geometry']]

def import_data():
    df = pd.read_csv('data/raw/amazon_sample.zip', nrows=1000)
    df = df.iloc[:, :-1]  # Drop last column
    df.rename(columns={'ship-state' : 'state'}, inplace=True)
    df['state'] = df['state'].str.title()
    df['state'].dropna(inplace=True)
    df['Date'] = pd.to_datetime(df["Date"], format="%m-%d-%y", errors="coerce")
    df['is_promotion'] = df['promotion-ids'].notna() # will capture both NA and empty string

    url = 'https://naciscdn.org/naturalearth/50m/cultural/ne_50m_admin_1_states_provinces.zip'
    india = gpd.read_file(url).query("iso_a2 == 'IN'")
    india.rename(columns={'name' : 'state'}, inplace=True)

    state_mapping = {
        'Dadra And Nagar': 'Dadra and Nagar Haveli and Daman and Diu',
        'New Delhi': 'Delhi',
        'Andaman & Nicobar ': 'Andaman and Nicobar',
        'Jammu & Kashmir ': 'Jammu and Kashmir',
        'Rj': 'Rajasthan'
    }

    # Rename values in df
    df['state'] = df['state'].replace(state_mapping)

    return df, india

df, india = import_data()

# Toggle for promotions
promotion_toggle = dbc.Row(
    [
        dbc.Col(width="auto"),
        dbc.Col(
            dbc.Switch(
                id="promotion-toggle",
                value=False,  # Default is OFF (showing orders without promotions)
            ),
            width="auto"
        ),
    ],
    className="mb-3"
)

# Initiatlize the app
app = Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])
server = app.server

# Layout
app.layout = dbc.Container([
    html.Label("Promotions Only:", className="fw-bold mt-3", style={"color": "#34495e"}),
            dbc.Switch(id="promotion-toggle", value=False, className="ms-2"),
            html.Hr(),
    dvc.Vega(id='sales', spec={}),
])

# Server side callbacks/reactivity
@callback(
    Output('sales', 'spec'),
    Input("promotion-toggle", "value"),
)
def create_sales_chart(promo_filter):
    # Apply promotion filter
    if promo_filter:
        selection = df.query('(is_promotion == True)')
    else:
        selection = df.query('(is_promotion == False)')
    sales = alt.Chart(selection, width='container').mark_line().encode(
                x=alt.X('yearmonth(Date):T', title='Month'),
                y=alt.Y('sum(Amount):Q', title='Total Amount')
            ).to_dict(format='vega')

    return sales

# Run the app/dashboard
if __name__ == '__main__':
    app.run(debug=True)