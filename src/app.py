import dash_bootstrap_components as dbc
import callbacks
from dash import Dash, html, dcc
from data import import_data, import_geojson, preprocess_data
from components import create_title, create_metric_1, create_metric_2, create_metric_3, create_footer, create_date_slider, create_promotion_toggle, create_fulfillment_radio, create_status_checkbox

# Initialize the app
app = Dash(__name__, external_stylesheets=[dbc.themes.YETI])
server = app.server

# Import data
df = import_data()
india = import_geojson()

# Preprocessed data
preprocessed_data = preprocess_data(df)
status_mapping = preprocessed_data["status_mapping"]
month_labels = preprocessed_data["month_labels"]
total_revenue_current = preprocessed_data["total_revenue_current"]
revenue_mom_change = preprocessed_data["revenue_mom_change"]
total_quantity_current = preprocessed_data["total_quantity_current"]
quantity_mom_change = preprocessed_data["quantity_mom_change"]
completion_rate_current = preprocessed_data["completion_rate_current"]
completion_rate_mom_change = preprocessed_data["completion_rate_mom_change"]

# Create Ccmponents
# Header / Title
title = create_title()

# Metrics Cards using computed values
metric_1 = create_metric_1(total_revenue_current, revenue_mom_change)
metric_2 = create_metric_2(total_quantity_current, quantity_mom_change)
metric_3 = create_metric_3(completion_rate_current, completion_rate_mom_change)

metrics = dbc.Row([
    dbc.Col(metric_1),
    dbc.Col(metric_2),
    dbc.Col(metric_3)
], id='metrics')

# Footer
footer = create_footer()

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
                dcc.Graph(id='map', figure={})]),
            dbc.Row([
                dbc.Col([dcc.Graph(id='sales', figure={})]),
                dbc.Col([dcc.Graph(id='product', figure={})])
            ])
        ], id='visuals')

# Layout
app.layout = dbc.Container([
    dcc.Store(id="filter_condition", data={}),
    # Title
    dbc.Row([
        dbc.Col(title, width=12)
    ], className="mb-3"),  # Add margin-bottom for spacing

    # Filters on the left, Metrics & Charts stacked in a single column
    dbc.Row([
        dbc.Col(filters, width=3),  # Filters stay on the left
        dbc.Col([  # Metrics and Charts in one column to align properly
            metrics,
            html.Hr(),  # Horizontal line for better separation
            visuals  # Charts and map appear directly below the metrics
        ], width=9)
    ], align="start", className="mb-4"), 
    footer
], fluid=True)

# Run the app/dashboard
if __name__ == '__main__':
    app.run(debug=False)