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

def format_indian_rupees(amount):
    """
    Format a number in the Indian Rupee system with proper separators.
    
    Args:
        amount (float): The amount to format.
    
    Returns:
        str: Formatted string (e.g., ₹9,87,200 for 987200).
    """
    if amount is None or amount == 0:
        return "₹0"
    
    # Convert to absolute integer value and string
    amount_str = str(abs(int(amount)))
    length = len(amount_str)
    
    # Handle numbers with 3 or fewer digits
    if length <= 3:
        return f"₹{amount_str}"
    
    # Take the last three digits
    first_part = amount_str[-3:]
    # Take the remaining digits
    rest = amount_str[:-3]
    
    # Group the remaining digits in pairs of two from right to left
    rest_formatted = ""
    for i in range(len(rest)):
        if i % 2 == 0 and i != 0:
            rest_formatted = "," + rest_formatted
        rest_formatted = rest[-i-1] + rest_formatted
    
    # Combine the parts
    formatted_amount = rest_formatted + "," + first_part if rest else first_part
    
    # Add rupee symbol and handle negative numbers
    return f"₹{'-' + formatted_amount if amount < 0 else formatted_amount}"




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
    Create the date slider component for selecting a range of months.

    Args:
        month_labels (dict): Mapping of month labels for the date slider.

    Returns:
        dcc.RangeSlider: Range slider component.
    """
    return dcc.RangeSlider(
        id="date-slider",
        min=0,
        max=len(month_labels) - 1,
        value=[0, len(month_labels) - 1],  # Default: full range selection
        marks={i: {"label": label, "style": {"color": "white"}} for i, label in month_labels.items()},
        step=1,
        tooltip={"placement": "bottom", "always_visible": True},
    )


def create_week_selector(week_labels):
    """
    Create a range slider for selecting a start and end week range.
    
    Args:
        week_labels (dict): Mapping of week labels (e.g., {0: '2022-03-28/2022-04-03', ...}).
    
    Returns:
        dcc.RangeSlider: Range slider component for week selection.
    """
    max_index = max(week_labels.keys())  # Get the maximum index for the slider range
    return dcc.RangeSlider(
        id="week-range-slider",
        min=0,
        max=max_index,
        marks={i: {"label": str(i), "style": {"color": "white"}} for i in week_labels.keys()},
        step=1,
        value=[3, 9],  # Default range
        tooltip={"placement": "bottom", "always_visible": True}
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

def create_time_radio():
    """
    Create the time granularity radio button component for the dashboard.
    
    Returns:
        dbc.Col: Fulfillment radio button component.
    """         
    return dbc.Col([
        dbc.RadioItems(
            id="time_granularity",
            options=[
                {"label": " Monthly", "value": "Monthly"},
                {"label": " Weekly", "value": "Weekly"}
            ],
            value="Monthly",
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

def create_filters(month_labels, week_labels, status_mapping):
    """
    Create the filters component for the dashboard.
    
    Args:
        month_labels (dict): Mapping of month labels for the date slider.
        week_labels (dict): Mapping of week labels for the week selector.
        status_mapping (dict): Mapping of order statuses.
    
    Returns:
        dbc.Col: Filters component.
    """
    date_slider = create_date_slider(month_labels)
    week_selector = create_week_selector(week_labels)
    time_radio = create_time_radio()
    promotion_toggle = create_promotion_toggle()
    fulfillment_radio = create_fulfillment_radio()
    status_checkbox = create_status_checkbox(status_mapping)

    return dbc.Col([
        dbc.Card(
            dbc.CardBody([
                html.H2("Amazon Sales Dashboard", className="text-center mb-4", 
                        style={"color": "white", "font-weight": "bold"}),

                html.Label("Time Granularity:", className="fw-bold mt-3", style={"color": "white", "font-size": "15px"}),
                time_radio,
                html.Hr(style={"border-top": "1px solid white"}),

                html.Label("Select Monthly Range:", className="fw-bold", style={"color": "white !important"}, id='month-label'),
                html.Div(id='date-slider-container', children=date_slider),
                html.Label("Select Weekly Range:", className="fw-bold", style={"color": "white !important"}, id='week-label'),
                html.Div(id='week-selector-container', children=week_selector, style={'display': 'none'}),
                html.Hr(style={"border-top": "1px solid white"}),

                html.Label("Promotions Only:", className="fw-bold mt-3", style={"color": "white"}),
                promotion_toggle,
                html.Hr(style={"border-top": "1px solid white"}),

                html.Label("Fulfillment Type:", className="fw-bold mt-3", style={"color": "white"}),
                fulfillment_radio,
                html.Hr(style={"border-top": "1px solid white"}),

                html.Label("Order Status:", className="fw-bold mt-3", style={"color": "white"}),
                status_checkbox,
                html.Br(),

                html.Div(id="filtered-data", style={"font-size": "12px", "font-style": "italic", "color": "white"})
            ]),
            className="shadow-sm rounded-3 p-4",
            style={
                "background-color": "#2C3E50",  # Dark blue background
                "border": "none",
                "width": "320px",  # Adjust width
                "color": "white",
                "height": "100vh"  # Make it full height
            }
        )
    ], width="auto", style={"padding-right": "10px"})  # Reduce gap between filters and charts

        

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
        ], style={"margin-top": "5px"}) 

def create_state_summary_graph():
    return dbc.Card([
        dbc.CardHeader('Sales by State'),
        dbc.CardBody(dcc.Graph(id='state_summary', figure={}))
    ], style={"margin-top": "5px"})

def create_sales_graph():
    return dbc.Card([
        dbc.CardHeader(id='sales-chart-header', children='Monthly Sales'),
        dbc.CardBody(dcc.Graph(id='sales', figure={})), 
    ], style={"margin-top": "5px"}) 

def create_product_graph():
    return dbc.Card([
        dbc.CardHeader('Sales Breakdown'),
        dbc.CardBody(dcc.Graph(id='product', figure={}))
    ], style={"margin-top": "5px"}) 

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