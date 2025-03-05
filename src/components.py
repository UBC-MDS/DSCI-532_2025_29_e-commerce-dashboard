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
        main_branch = repo.heads.main
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
    return dbc.Row(html.H1("Sales Dashboard"), className="bg-secondary text-black p-2 mb-4 text-center", id='title')

def create_metric_1(total_revenue_current, revenue_mom_change):
    """
    Create the first metric card for total revenue.
    
    Args:
        total_revenue_current (float): Current total revenue.
        revenue_mom_change (float): Month-over-month change in revenue.
    
    Returns:
        dbc.Card: Metric card for total revenue.
    """
    return dbc.Card(
        dbc.CardBody(
            [
                html.H3("Revenue", className="card-title", style={"font-size": "18px"}),
                html.H1(f"${format_large_num(total_revenue_current)}", className="card-text", style={"font-size": "30px", "font-weight": "bold"}),
                html.Small(f"Compared to previous month: {revenue_mom_change:+.1%}",
                           className="card-text text-muted", style={"font-size": "14px"})
            ]
        ),
        style={"width": "18rem", "text-align": "center", "background-color": "#f8f9fa", "border-radius": "10px"}
    )

def create_metric_2(total_quantity_current, quantity_mom_change):
    """
    Create the second metric card for total quantity sold.
    
    Args:
        total_quantity_current (float): Current total quantity sold.
        quantity_mom_change (float): Month-over-month change in quantity sold.
    
    Returns:
        dbc.Card: Metric card for total quantity sold.
    """
    return dbc.Card(
        dbc.CardBody(
            [
                html.H3("Quantity Sold", className="card-title", style={"font-size": "18px"}),
                html.H1(f"{format_large_num(total_quantity_current)}", className="card-text", style={"font-size": "30px", "font-weight": "bold"}),
                html.Small(f"Compared to previous month: {quantity_mom_change:+.1%}",
                           className="card-text text-muted", style={"font-size": "14px"})
            ]
        ),
        style={"width": "18rem", "text-align": "center", "background-color": "#f8f9fa", "border-radius": "10px"},
    )

def create_metric_3(completion_rate_current, completion_rate_mom_change):
    """
    Create the third metric card for order completion rate.
    
    Args:
        completion_rate_current (float): Current order completion rate.
        completion_rate_mom_change (float): Month-over-month change in completion rate.
    
    Returns:
        dbc.Card: Metric card for order completion rate.
    """
    return dbc.Card(
        dbc.CardBody(
            [
                html.H3("Completed Orders", className="card-title", style={"font-size": "18px"}),
                html.H1(f"{completion_rate_current:.2f}%", className="card-text", style={"font-size": "30px", "font-weight": "bold"}),
                html.Small(f"Compared to previous month: {completion_rate_mom_change:+.1f}%",
                           className="card-text text-muted", style={"font-size": "14px"})
            ]
        ),
        style={"width": "18rem", "text-align": "center", "background-color": "#f8f9fa", "border-radius": "10px"},
    )

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
            options=[key for key, _ in status_mapping.items()],
            value=["Shipped"],  # Default selection
            inline=False  # Display vertically
        )
    ])