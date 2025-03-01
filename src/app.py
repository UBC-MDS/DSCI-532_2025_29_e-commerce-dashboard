from dash import Dash, html, dcc, Input, Output, callback
import dash_bootstrap_components as dbc
import dash_vega_components as dvc
import pandas as pd
import altair as alt
import geopandas as gpd

alt.data_transformers.enable('vegafusion')

def import_data():
    df = pd.read_csv('data/raw/amazon_sample.csv', nrows=1000)
    df = df.iloc[:, :-1]  # Drop last column
    df.rename(columns={'ship-state' : 'state'}, inplace=True)
    df['state'] = df['state'].str.title()
    df['state'].dropna(inplace=True)
    df['Date'] = pd.to_datetime(df['Date'])

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

    # ship_states = set(df['state'].unique())
    # india_states = set(india['state'].unique())
    # missing_in_india = ship_states - india_states
    # missing_in_ship = india_states - ship_states

    # print("States in df but not in india:", missing_in_india)
    # print("States in india but not in df:", missing_in_ship)

    print(df.columns)
    return df, india

# Data
df, india = import_data()

# Components
# Charts
map = alt.Chart(india, width='container').mark_geoshape(stroke='grey').encode(
        ).add_params(
            alt.selection_point(fields=["state"], name="selected_states")
        ).to_dict(format='vega')

# Initiatlize the app
app = Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])
server = app.server

# Layout
app.layout = dbc.Container([
    dbc.Col(dvc.Vega(id='map', spec=map, signalsToObserve=['selected_states'])),
    dbc.Col(dvc.Vega(id='sales', spec={}))
])

# Server side callbacks/reactivity
@app.callback(
    Output("sales", "spec"),
    Input("map", "signalData"),
    prevent_initial_call=True
)
def create_sales_chart(signal_data):
    print(signal_data)
    if not signal_data or not signal_data['selected_states']:
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

# Run the app/dashboard
if __name__ == '__main__':
    app.run(debug=False)