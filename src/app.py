from dash import Dash, html, dcc, Input, Output, callback
import dash_bootstrap_components as dbc
import pandas as pd
import geopandas as gpd
import plotly.express as px
import plotly.graph_objects as go
from git import Repo
from datetime import datetime

# Import sales data for dashboard
def import_data():
    df = pd.read_csv('data/raw/amazon_sample.zip', nrows=1000)
    df = df.iloc[:, :-1]  # Drop last column
    df.rename(columns={'ship-state': 'state'}, inplace=True)
    df['state'] = df['state'].str.title()
    df['state'].dropna(inplace=True)
    df['Date'] = pd.to_datetime(df["Date"], format="%m-%d-%y", errors="coerce")

    # Extract year-month for aggregation
    df["year_month"] = df["Date"].dt.to_period("M").astype(str)

    # Add flag for promotions
    df['is_promotion'] = df['promotion-ids'].notna()  # will capture both NA and empty string

    # Mapping to rename state names in sales data
    state_mapping = {
        'Dadra And Nagar': 'Dadra and Nagar Haveli and Daman and Diu',
        'New Delhi': 'Delhi',
        'Andaman & Nicobar ': 'Andaman and Nicobar',
        'Jammu & Kashmir ': 'Jammu and Kashmir',
        'Rj': 'Rajasthan'
    }

    df['state'] = df['state'].replace(state_mapping)

    return df

# Import geojson file for India
def import_geojson():
    url = 'https://naciscdn.org/naturalearth/50m/cultural/ne_50m_admin_1_states_provinces.zip'
    india = gpd.read_file(url).query("iso_a2 == 'IN'")
    india.rename(columns={'name': 'state'}, inplace=True)

    return india

# Function to format numeric values
def format_large_num(value):
    value = float('{:.3g}'.format(value))
    magnitude = 0
    while abs(value) >= 1000:
        magnitude += 1
        value /= 1000.0
    return '{}{}'.format('{:f}'.format(value).rstrip('0').rstrip('.'), ['', 'K', 'M', 'B', 'T'][magnitude])

# Function to get the latest commit date
def get_latest_commit_date():
    try: #included to handle any error gracefully
        repo = Repo(".") 
        latest_commit = repo.head.commit
        commit_date = datetime.fromtimestamp(latest_commit.committed_date)
        return commit_date.strftime("%B %d, %Y")  
    except Exception as e:
        print(f"Error fetching commit date: {e}")
        return "Unknown Date"
    
# Initialize the app
app = Dash(__name__, external_stylesheets=[dbc.themes.YETI])
server = app.server

# Data
df = import_data()
india = import_geojson()

status_mapping = {
    'Cancelled': ['Cancelled'],
    'Pending': ['Pending', 'Pending - Waiting for Pick Up', 'Shipping'],
    'Shipped': ['Shipped', 'Shipped - Damaged', 'Shipped - Delivered to Buyer',
        'Shipped - Lost in Transit', 'Shipped - Out for Delivery',
        'Shipped - Picked Up', 'Shipped - Rejected by Buyer',
        'Shipped - Returned to Seller', 'Shipped - Returning to Seller'],
}

# Extract all unique year-month values from the full dataset
all_months = df["year_month"].unique()
all_months_sorted = sorted(all_months)  # Ensure months are sorted

# Create a mapping of months to index positions for the slider
month_labels = {i: label for i, label in enumerate(all_months_sorted)}

# Filter only last 2 months
df_month_values = (
    df.groupby('year_month').agg({'Amount': 'sum', 'Qty': 'sum'})
    .sort_index()
)[-2:]

# Create list of the last 2 months and filter for metric
last2_months = df_month_values.index.to_list()
df_metric = df[df["year_month"].isin(last2_months)]

# Compute Revenue Change over the last 2 months
revenue_mom = df_month_values[['Amount']]

# Ensure we have at least two months of data before computing the percentage change
if len(revenue_mom) > 1:
    revenue_mom_change = (revenue_mom.pct_change().iloc[-1].item())
else:
    revenue_mom_change = 0  # Default to 0% change if not enough data

# Compute Quantity Sold Change
qty_mom = df_month_values[['Qty']]

# Ensure we have at least two months of data before computing the percentage change
if len(qty_mom) > 1:
    quantity_mom_change = (qty_mom.pct_change().iloc[-1].item())
else:
    quantity_mom_change = 0  # Default to 0% change if not enough data

total_revenue_current = revenue_mom.iloc[-1].item()
total_quantity_current = qty_mom.iloc[-1].item()

# Compute Completed Orders Percentage
completed_status = ["Shipped", "Shipped - Delivered to Buyer", "Shipped - Picked Up", "Shipped - Out for Delivery"]
df.loc[:, "order_status_category"] = df["Status"].apply(lambda x: "Completed" if x in completed_status else "Uncompleted")

monthly_counts = df.groupby("year_month")["order_status_category"].count()
completed_counts = df[df["order_status_category"] == "Completed"].groupby("year_month")["order_status_category"].count()

# Get the completion rate, ensure values sorted by month
completion_rate = (completed_counts / monthly_counts).sort_index() * 100
completion_rate_current = completion_rate.iloc[-1]

# Ensure 2+ months worth of data exists before accessing
if len(completion_rate.index) > 1:
    completion_rate_prev = completion_rate.iloc[-2]
    completion_rate_mom_change = ((completion_rate_current - completion_rate_prev) / completion_rate_prev) * 100
else:
    completion_rate_mom_change = 0  # Default to 0% if only one month of data

# Components
# Header / Title
title = dbc.Row(html.H1("Sales Dashboard"), className="bg-secondary text-black p-2 mb-4 text-center", id='title')

# Metrics Cards using computed values
metric_1 = dbc.Card(
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

metric_2 = dbc.Card(
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

metric_3 = dbc.Card(
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
metrics = dbc.Row([
    dbc.Col(metric_1),
    dbc.Col(metric_2),
    dbc.Col(metric_3)
], id='metrics')

# Get the dynamic date
footer_date = get_latest_commit_date()

## Footer - This includes title, group number and names of members, last updated date
footer = dbc.Row(
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
## Filters

# Date (Month) Slider
date_slider = dcc.Slider(
    id="date-slider",
    min=0,
    max=len(all_months_sorted) - 1,
    value=len(all_months_sorted) - 1,  # Default: latest month
    marks={i: label for i, label in month_labels.items()},
    step=None,
    tooltip={"placement": "bottom", "always_visible": True},
)

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

# Fulfillment Type Radio Button
fulfillment_radio = dbc.Col([
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

# Checkbox for order status, use grouped statuses
status_checkbox = dbc.Col([
    dcc.Checklist(
        id="status-checkbox",
        options=[key for key, _ in status_mapping.items()],
        value=["Shipped"],  # Default selection
        inline=False  # Display vertically
    )
])

# Filters section
filters = dbc.Col([
    dbc.Card(
        dbc.CardBody([
            html.H4("Filters", className="text-center mb-4", style={"font-weight": "bold", "color": "#2c3e50"}),

            html.Label("Select Month:", className="fw-bold", style={"color": "#34495e"}),
            dcc.Slider(
                id="date-slider",
                min=0,
                max=len(df["year_month"].unique()) - 1,
                value=len(df["year_month"].unique()) - 1,
                marks={i: label for i, label in enumerate(sorted(df["year_month"].unique()))},
                step=None,
                tooltip={"placement": "bottom", "always_visible": True},
            ),
            html.Hr(),

            html.Label("Promotions Only:", className="fw-bold mt-3", style={"color": "#34495e"}),
            dbc.Switch(id="promotion-toggle", value=False, className="ms-2"),
            html.Hr(),

            html.Label("Fulfillment Type:", className="fw-bold mt-3", style={"color": "#34495e"}),
            dbc.RadioItems(
                id="fulfillment-radio",
                options=[
                    {"label": " Amazon", "value": "Amazon"},
                    {"label": " Merchant", "value": "Merchant"},
                    {"label": " Both", "value": "Both"}
                ],
                value="Both",
                inline=False,
                className="d-flex flex-column mt-2"
            ),
            html.Hr(),

            html.Label("Order Status:", className="fw-bold mt-3", style={"color": "#34495e"}),
            dbc.Checklist(
                id="status-checkbox",
                options=[key for key, _ in status_mapping.items()],
                inline=False,
                className="mt-2"
            ),
            html.Br(),

            html.Div(id="filtered-data", style={"font-size": "8px", "font-style": "italic"})
        ]),
        className="shadow-sm rounded-3 p-4",
        style={"background-color": "#ffffff", "border": "1px solid #ddd", "width": "350px"}  # Reduced width
    )
], width="auto", className="d-flex justify-content-center")

# Create Plotly map
state_sales = df.groupby('state')['Amount'].sum().reset_index()
fig = px.choropleth(
    state_sales,
    geojson=india.__geo_interface__,
    locations='state',
    featureidkey="properties.state",
    color='Amount',
    hover_name='state',
    hover_data=['Amount'],
    title="Sales by State and Territories",
    color_continuous_scale=px.colors.sequential.Bluyl  # Change the color theme
)
fig.update_geos(fitbounds="locations", visible=False)
fig.update_layout(
    coloraxis_showscale=False,
    modebar=dict(remove=['select', 'lasso2d'])
)

# Visuals
visuals = dbc.Row([
        dbc.Row([
            dcc.Graph(id='map', figure=fig)]),
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

# Server side callbacks/reactivity
@app.callback(
    Output("filtered-data", "children"),  # Debugging output
    Output("filter_condition", "data"),
    Input("date-slider", "value"),
    Input("promotion-toggle", "value"),
    Input("fulfillment-radio", "value"),
    Input("status-checkbox", "value"),
    Input("map", "clickData"),
)
def update_filtered_data(selected_index, promo_filter, fulfillment_filter, selected_statuses, click_data):
    # Convert slider index to corresponding year-month
    selected_date = month_labels.get(selected_index, None)

    if not selected_date:
        return "No selection", ""

    # set end date to proper date
    filter_end_date = pd.to_datetime(f'{selected_date}-01') + pd.DateOffset(months=1)
    filter_condition = f'(Date < "{filter_end_date}")'

    # Apply promotion filter
    if promo_filter:
        filter_condition += ' & (is_promotion == True)'

    # Apply fulfillment filter if selection is not Both
    if fulfillment_filter != "Both":  # If not "Both", filter accordingly
        filter_condition += f' & (Fulfilment == "{fulfillment_filter}")'

    # Apply order status filter
    if selected_statuses:
        filter_statuses = [item for key, values in status_mapping.items() for item in values if key in selected_statuses]
        filter_statuses_str = ', '.join([f'"{status}"' for status in filter_statuses])
        filter_condition += f' & (Status in [{filter_statuses_str}])'

    if click_data and 'points' in click_data:
        state = click_data['points'][0]['location']
        filter_condition += f' & (state == "{state}")'

    # Store the filtered dataset
    filtered_df = df.query(filter_condition)

    return f"Showing {len(filtered_df):,.0f} records up to {selected_date}.", filter_condition

# @callback(
#     Output("map", "figure"),
#     Input("filter_condition", "data")
# )
# def create_map(query):
#     states = df['state'].unique()
#     state_sales = df.query(query).groupby('state')['Amount'].sum().reset_index()

#     # Populate states with no data with 0
#     all_states = pd.DataFrame({'state': states})
#     state_sales = all_states.merge(state_sales, on='state', how='left').fillna(0)

#     fig = px.choropleth(
#         state_sales,
#         geojson=india.__geo_interface__,
#         locations='state',
#         featureidkey="properties.state",
#         color='Amount',
#         hover_name='state',
#         hover_data=['Amount'],
#         title="Sales by State and Territories",    
#         color_continuous_scale=px.colors.sequential.Bluyl  # Change the color theme
#     )
#     fig.update_geos(fitbounds="locations", visible=False)
#     fig.update_layout(coloraxis_showscale=False)

#     return fig

@callback(
    Output("sales", "figure"),
    Input("filter_condition", "data")
    # prevent_initial_call=True
)
def create_sales_chart(query):
    try:
        selection = df.query(query)
        # Group by year_month and sum the Amount
        selection = selection.groupby('year_month')['Amount'].sum().reset_index()
        selection['year_month'] = pd.to_datetime(selection['year_month'])
        sales = px.line(
            selection,
            x='year_month',
            y='Amount',
            title='Monthly Sales',
            labels={'year_month': 'Month', 'Amount': 'Total Sales'},
            line_shape='linear'
        )
        # Disable pan and zoom
        sales.update_layout(
            xaxis=dict(fixedrange=True),
            yaxis=dict(fixedrange=True)
        )
        return sales
    except Exception as e:
        print(f"Error in create_sales_chart: {e}")
        return go.Figure(data=[go.Scatter(x=[], y=[], mode='text', text=f"Error: {e}")])

@callback(
    Output("product", "figure"),
    Input("filter_condition", "data")
    # prevent_initial_call=True
)
def create_product_chart(query):
    try:
        selection = df.query(query)
        selection = selection.groupby('Category')['Amount'].sum().reset_index()
        total_amount = selection['Amount'].sum()
        selection['Percentage'] = (selection['Amount'] / total_amount) * 100

        product = px.pie(
            selection,
            values='Amount',
            names='Category',
            title='Product Categories',
            hover_data=['Amount', 'Percentage'],
            labels={'Amount': 'Total Amount', 'Percentage': 'Percentage'}
        )
        product.update_traces(textposition='inside', textinfo='percent+label')

        return product
    except Exception as e:
        print(f"Error in create_product_chart: {e}")
        return go.Figure(data=[go.Scatter(x=[], y=[], mode='text', text=f"Error: {e}")])

# Run the app/dashboard
if __name__ == '__main__':
    app.run(debug=False)