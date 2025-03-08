import dash_bootstrap_components as dbc
from dash import html, dcc
from git import Repo
from datetime import datetime

# Function to format numeric values
def format_large_num(value):
    """
    Format large numeric values with appropriate suffixes (K, M, B, T).
    
    Args:
        value (float): Numeric value to format.
    
    Returns:
        str: Formatted numeric value with suffix.
    """
    value = float('{:.3g}'.format(value))
    magnitude = 0
    while abs(value) >= 1000:
        magnitude += 1
        value /= 1000.0
    return '{}{}'.format('{:f}'.format(value).rstrip('0').rstrip('.'), ['', 'K', 'M', 'B', 'T'][magnitude])

# Function to get the latest commit date on the main branch
def get_latest_commit_date():
    """
    Get the date of the latest commit on the main branch in the repository.
    
    Returns:
        str: Latest commit date in "Month Day, Year" format.
    """
    try:
        repo = Repo(".")
        main_branch = repo.branches['main']
        latest_commit = main_branch.commit
        commit_date = datetime.fromtimestamp(latest_commit.committed_date)
        return commit_date.strftime("%B %d, %Y")
    except Exception as e:
        print(f"Error fetching commit date: {e}")
        return "Unknown Date"

def create_title():
    """
    Create the title component for the dashboard.
    
    Returns:
        dbc.Row: Title component.
    """
    return dbc.Row(html.H1("Amazon Sales Dashboard"), className="bg-secondary text-black p-2 mb-4 text-center", id='title')

def format_mom_change(value):
    """
    Format Month-over-Month (MoM) change with color and arrow indicators.

    Args:
        value (float): The month-over-month percentage change.

    Returns:
        html.Small: Styled HTML component indicating the MoM change.
    """
    color = "#FFA500" if value > 0 else "#87CEEB" if value < 0 else "black"  # Orange for positive, Sky Blue for negative
    arrow = "▲" if value > 0 else "▼" if value < 0 else "▪"  # Arrows for trends

    return html.Small(f" {arrow} {value:+.1f}%", 
                      className="card-text text-muted", 
                      style={"font-size": "14px", "color": color})

def create_footer():
    """
    Create the footer component for the dashboard.
    
    Returns:
        dbc.Row: Footer component.
    """
    footer_date = get_latest_commit_date()

    return dbc.Row(
        dbc.Col(
            html.P([
                html.A("E-Commerce Sales Dashboard:", href="https://github.com/UBC-MDS/DSCI-532_2025_29_e-commerce-dashboard", target="_blank"),
                " A tool to analyze sales performance and market trends for e-commerce clothing stores. ",
                "Created by Group 29 - Jenson, Shashank, Sienko, Yajing. ",
                f" | Last Updated: {footer_date}"
            ], className="text-muted text-center small")
        ),
        className="mt-4"  
    )

def create_date_slider(month_labels):
    """
    Create the date slider component for the dashboard.
    
    Args:
        month_labels (dict): Mapping of month labels for the date slider.
    
    Returns:
        dcc.Slider: Date slider component.
    """
    return dcc.Slider(
        id="date-slider",
        min=0,
        max=len(month_labels) - 1,
        value=len(month_labels) - 1,  # Default: latest month
        marks={i: label for i, label in month_labels.items()},
        step=None,
        tooltip={"placement": "bottom", "always_visible": True},
    )

def create_promotion_toggle():
    """
    Create the promotion toggle switch component for the dashboard.
    
    Returns:
        dbc.Row: Promotion toggle switch component.
    """
    return dbc.Row(
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

def create_fulfillment_radio():
    """
    Create the fulfillment radio button component for the dashboard.
    
    Returns:
        dbc.Col: Fulfillment radio button component.
    """
    return dbc.Col([
        dbc.RadioItems(
            id="fulfillment-radio",
            options=[
                {"label": " Amazon", "value": "Amazon"},
                {"label": " Merchant", "value": "Merchant"},
                {"label": " Both", "value": "Both"}  # New option added
            ],
            value="Both",  # Default selection to show all by default
            inline=False,
            className="mt-2"
        )
    ], width=3)

def create_status_checkbox(status_mapping):
    """
    Create the status checkbox component for the dashboard.
    
    Args:
        status_mapping (dict): Mapping of order statuses.
    
    Returns:
        dbc.Col: Status checkbox component.
    """
    return dbc.Col([
        dcc.Checklist(
            id="status-checkbox",
            options=[{"label": f" {key}", "value": key} for key in status_mapping.keys()],
            value=["Shipped"],  # Default selection
            inline=False  # Display vertically
        )
    ])

def create_filters(month_labels, status_mapping):
    """
    Create the filters component for the dashboard.
    
    Args:
        month_labels (dict): Mapping of month labels for the date slider.
        status_mapping (dict): Mapping of order statuses.
    
    Returns:
        dbc.Col: Filters component.
    """
    date_slider = create_date_slider(month_labels)
    promotion_toggle = create_promotion_toggle()
    fulfillment_radio = create_fulfillment_radio()
    status_checkbox = create_status_checkbox(status_mapping)

    return dbc.Col([
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

def create_metrics():
    """
    Create the metrics component for the dashboard.
    
    Returns:
        dbc.Row: Metrics component.
    """
    return dbc.Row([
        dbc.Col(dbc.Card(dbc.CardBody(id="metric-1"), style={
            "width": "94%", "text-align": "center", "background-color": "#f8f9fa", "border-radius": "10px"}), width=4),
        dbc.Col(dbc.Card(dbc.CardBody(id="metric-2"), style={
            "width": "94%", "text-align": "center", "background-color": "#f8f9fa", "border-radius": "10px"}), width=4),
        dbc.Col(dbc.Card(dbc.CardBody(id="metric-3"), style={
            "width": "94%", "text-align": "center", "background-color": "#f8f9fa", "border-radius": "10px"}), width=4)
    ], id='metrics', justify="center")

def create_map_graph():
    return dbc.Card([
        dbc.CardHeader('Map of India'),
        dbc.CardBody(dcc.Graph(id='map', figure={}))
        ]) 

def create_state_summary_graph():
    return dbc.Card([
        dbc.CardHeader('Title'),
        dbc.CardBody(dcc.Graph(id='state_summary', figure={}))
    ])

def create_sales_graph():
    return dbc.Card([
        dbc.CardHeader('Weekly Sales'),
        dbc.CardBody(dcc.Graph(id='sales', figure={})), 
    ], style={"margin-top": "15px"}) 

def create_product_graph():
    return dbc.Card([
        dbc.CardHeader('Sales Breakdown'),
        dbc.CardBody(dcc.Graph(id='product', figure={}))
    ], style={"margin-top": "15px"}) 

def create_visuals():
    return dbc.Row([
                dbc.Row([
                    dbc.Col([create_map_graph()], className="chart_column"),
                    dbc.Col([create_state_summary_graph()], className="chart_column")
                    ]),
                dbc.Row([
                    dbc.Col([create_sales_graph()], className="chart_column"),
                    dbc.Col([create_product_graph()], className="chart_column")
                ])
            ], id='visuals')