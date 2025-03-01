from dash import Dash, html, dcc, Input, Output, callback
import dash_bootstrap_components as dbc
import dash_vega_components as dvc
import pandas as pd
import altair as alt
import geopandas as gpd

alt.data_transformers.enable('vegafusion')

url = 'https://naciscdn.org/naturalearth/50m/cultural/ne_50m_admin_1_states_provinces.zip'
world_regions = gpd.read_file(url)[['wikipedia', 'name', 'admin', 'postal', 'latitude', 'longitude', 'geometry']]

# Initiatlize the app
app = Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])
server = app.server

# Layout
app.layout = dbc.Container([
    dcc.Dropdown(id='country', value='India', options=world_regions['admin'].unique()),
    dvc.Vega(id='map', spec={}, signalsToObserve=['select_region']),
    # dcc.Markdown(id='chart-selection')
    html.Div(id='chart-selection')
])

# Server side callbacks/reactivity
@callback(
    Output('map', 'spec'),
    Input('country', 'value'),
)
def create_map(country):
    select_region = alt.selection_point(fields=['name'], name='select_region')
    return alt.Chart(world_regions.query(f'admin == "{country}"'), width=600, height=500).mark_geoshape(stroke='white').encode(
        tooltip='name',
        color=alt.Color('name').scale(scheme='tableau20'),  # To avoid repeating colors
        opacity=alt.condition(select_region, alt.value(0.9), alt.value(0.3))
    ).add_params(
        select_region
    ).to_dict(format="vega")

@callback(
    Output('chart-selection', 'children'),
    Input('map', 'signalData'),
)
def print_selection(clicked_region):
    print(clicked_region)  # So that you can see the full dictionary
    if clicked_region and 'name' in clicked_region['select_region']:
        return f'{clicked_region["select_region"]["name"]}'

# Run the app/dashboard
if __name__ == '__main__':
    app.run(debug=False)