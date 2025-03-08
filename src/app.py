import dash_bootstrap_components as dbc
from dash import Dash, html, dcc
from .data import import_data, import_geojson, preprocess_data
from .components import create_title, create_footer, create_filters, create_metrics, create_visuals

# Initialize the app
app = Dash(__name__, external_stylesheets=[dbc.themes.YETI])
server = app.server

# Import data
df = import_data('data/amazon_sample.zip')
india = import_geojson('https://naciscdn.org/naturalearth/50m/cultural/ne_50m_admin_1_states_provinces.zip')

# Preprocessed data
preprocessed_data = preprocess_data(df)
status_mapping = preprocessed_data["status_mapping"]
month_labels = preprocessed_data["month_labels"]

# Create Components
title = create_title()
metrics = create_metrics()
filters = create_filters(month_labels, status_mapping)
visuals = create_visuals()
footer = create_footer()

<<<<<<< Updated upstream
# Filters
date_slider = create_date_slider(month_labels)
promotion_toggle = create_promotion_toggle()
fulfillment_radio = create_fulfillment_radio()
status_checkbox = create_status_checkbox(status_mapping)

filters = dbc.Col([
    dbc.Card(
        dbc.CardBody([
            html.H4("Filters", className="text-center mb-4", style={"font-weight": "bold", "color": "#2c3e50"}),

            html.Label("Select Month:", className="fw-bold", style={"color": "#34495e"}),
            date_slider,
            html.Hr(),

            html.Label("Promotions Only:", className="fw-bold mt-3", style={"color": "#34495e"}),
            promotion_toggle,
            html.Hr(),

            html.Label("Fulfillment Type:", className="fw-bold mt-3", style={"color": "#34495e"}),
            fulfillment_radio,
            html.Hr(),

            html.Label("Order Status:", className="fw-bold mt-3", style={"color": "#34495e"}),
            status_checkbox,
            html.Br(),

            html.Div(id="filtered-data", style={"font-size": "8px", "font-style": "italic"})
        ]),
        className="shadow-sm rounded-3 p-4",
        style={"background-color": "#ffffff", "border": "1px solid #ddd", "width": "350px"}  # Reduced width
    )
], width="auto", className="d-flex justify-content-center")

# Visuals
visuals = dbc.Row([
            dbc.Row([
                dbc.Col([dcc.Graph(id='map', figure={})]),
                dbc.Col([dcc.Graph(id='state_summary', figure={})])
                ]),
            dbc.Row([
                dbc.Col([dcc.Graph(id='sales', figure={})]),
                dbc.Col([dcc.Graph(id='product', figure={})])
            ])
        ], id='visuals')

=======
>>>>>>> Stashed changes
# Layout
app.layout = dbc.Container([
    dcc.Store(id="filter_condition", data={}),
    dbc.Row([
        dbc.Col(title, width=12)], className="mb-3"),
    dbc.Row([
        dbc.Col(filters, width=3),
        dbc.Col([metrics,
                 html.Hr(),
                 visuals], 
                 width=9)],align="start", className="mb-4"), 
    footer], 
    fluid=True)

# Import callbacks to register them with the app
from . import callbacks

# Run the app/dashboard
if __name__ == '__main__':
    app.run(debug=False)