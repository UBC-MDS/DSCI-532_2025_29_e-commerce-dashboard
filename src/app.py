import dash_bootstrap_components as dbc
from dash import Dash, html, dcc
from .data import import_data, import_geojson, preprocess_data
from .components import create_footer, create_filters, create_metrics, create_visuals
from flask_caching import Cache

# Initialize the app
app = Dash(
    __name__, 
    external_stylesheets=[dbc.themes.YETI],
    title="Amazon Sales Dashboard")
server = app.server

# Import data
df = import_data('data/amazon_in_sales.parquet')
india = import_geojson('https://naciscdn.org/naturalearth/50m/cultural/ne_50m_admin_1_states_provinces.zip')

# Preprocessed data
preprocessed_data = preprocess_data(df)
status_mapping = preprocessed_data["status_mapping"]
month_labels = preprocessed_data["month_labels"]
week_labels = preprocessed_data["week_labels"]

# Create Components
metrics = create_metrics()
filters = create_filters(month_labels, week_labels, status_mapping)
visuals = create_visuals()
footer = create_footer()

# Layout
app.layout = dbc.Container([
    dcc.Store(id="filter_condition", data={}),
    dbc.Row([
        dbc.Col(filters, width=3),
        dbc.Col([metrics, html.Br(), visuals], width=9, style={"margin-top": "10px"})],align="start", className="mb-4"), 
    footer], 
    fluid=True)

cache = Cache(
    app.server,
    config={
        'CACHE_TYPE': 'filesystem',
        'CACHE_DIR': 'tmp'
    }
)

# Import callbacks to register them with the app
from . import callbacks

# Run the app/dashboard
if __name__ == '__main__':
    app.run(debug=False)