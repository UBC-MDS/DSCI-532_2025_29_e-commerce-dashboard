from dash import Dash, html, dcc, Input, Output, callback
import dash_bootstrap_components as dbc
import pandas as pd
import plotly.express as px
import json
import zipfile

# Initialize the app
app = Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])
server = app.server

# Unzip and import data
with zipfile.ZipFile('data/raw/amazon_sample.zip', 'r') as z:
    with z.open('amazon_sample.csv') as f:
        df = pd.read_csv(f)
df = df.iloc[:, :-1]  # Drop last column
df['ship-state'] = df['ship-state'].str.title()

# Preprocessing data for dashboard
# Convert Date column to datetime
df["Date"] = pd.to_datetime(df["Date"], format="%m-%d-%y", errors="coerce")

# Extract year-month for aggregation
df["year_month"] = df["Date"].dt.to_period("M").astype(str)

# Filter only May and June 2022
df_metric = df[df["year_month"].isin(["2022-05", "2022-06"])]


# Compute Revenue Change (June vs May)
revenue_mom = df_metric.groupby("year_month")["Amount"].sum()

# Ensure we have at least two months of data before computing the percentage change
if len(revenue_mom) > 1:
    revenue_mom_change = (revenue_mom.pct_change().iloc[-1]) * 100
else:
    revenue_mom_change = 0  # Default to 0% change if not enough data


# Compute Quantity Sold Change
qty_mom = df_metric.groupby("year_month")["Qty"].sum()
# Ensure we have at least two months of data before computing the percentage change
if len(qty_mom) > 1:
    quantity_mom_change = (qty_mom.pct_change().iloc[-1]) * 100
else:
    quantity_mom_change = 0  # Default to 0% change if not enough data


total_revenue_june = revenue_mom["2022-06"]
total_quantity_june = qty_mom["2022-06"]

# Compute Completed Orders Percentage
completed_status = ["Shipped", "Shipped - Delivered to Buyer", "Shipped - Picked Up", "Shipped - Out for Delivery"]
df.loc[:, "order_status_category"] = df["Status"].apply(lambda x: "Completed" if x in completed_status else "Uncompleted")

monthly_counts = df.groupby("year_month")["order_status_category"].count()
completed_counts = df[df["order_status_category"] == "Completed"].groupby("year_month")["order_status_category"].count()
completion_rate = (completed_counts / monthly_counts) * 100
completion_rate_june = completion_rate["2022-06"]
# Ensure May data exists before accessing
if "2022-05" in completion_rate.index:
    completion_rate_may = completion_rate["2022-05"]
    completion_rate_mom_change = ((completion_rate_june - completion_rate_may) / completion_rate_may) * 100
else:
    completion_rate_mom_change = 0  # Default to 0% if May data is missing



# Pre-aggregate data for map visualization
sales = df.groupby('ship-state').sum(numeric_only=True).reset_index()
sales.rename(columns={'ship-state': 'State'}, inplace=True)

# Load map
with open('data/states_india.geojson') as f:
    geojson = json.load(f)

# Plot choropleth map
fig = px.choropleth(sales, 
                    geojson=geojson, 
                    locations='State', 
                    featureidkey="properties.st_nm",
                    color='Amount',
                    color_continuous_scale="GnBu",
                    range_color=(100000, 1000000),
                    labels={'Amount': 'Revenue'}
                   )
fig.update_geos(fitbounds="locations", visible=False)
fig.update_layout(margin={"r": 0, "t": 0, "l": 0, "b": 0})

# Components

# Header / Title
title = dbc.Row(html.H1("Sales Dashboard"))

# Metrics Cards using computed values
metric_1 = dbc.Card(
    dbc.CardBody(
        [
            html.H3("Revenue", className="card-title", style={"font-size": "18px"}),
            html.H1(f"${total_revenue_june:,.2f}", className="card-text", style={"font-size": "30px", "font-weight": "bold"}),
            html.Small(f"Compared to previous month: {revenue_mom_change:+.1f}%",
                       className="card-text text-muted", style={"font-size": "14px"})
        ]
    ),
    style={"width": "18rem", "text-align": "center", "background-color": "#f8f9fa", "border-radius": "10px"},
)

metric_2 = dbc.Card(
    dbc.CardBody(
        [
            html.H3("Quantity Sold", className="card-title", style={"font-size": "18px"}),
            html.H1(f"{total_quantity_june:,.0f}", className="card-text", style={"font-size": "30px", "font-weight": "bold"}),
            html.Small(f"Compared to previous month: {quantity_mom_change:+.1f}%",
                       className="card-text text-muted", style={"font-size": "14px"})
        ]
    ),
    style={"width": "18rem", "text-align": "center", "background-color": "#f8f9fa", "border-radius": "10px"},
)

metric_3 = dbc.Card(
    dbc.CardBody(
        [
            html.H3("Completed Orders", className="card-title", style={"font-size": "18px"}),
            html.H1(f"{completion_rate_june:.2f}%", className="card-text", style={"font-size": "30px", "font-weight": "bold"}),
            html.Small(f"Compared to previous month: {completion_rate_mom_change:+.1f}%",
                       className="card-text text-muted", style={"font-size": "14px"})
        ]
    ),
    style={"width": "18rem", "text-align": "center", "background-color": "#f8f9fa", "border-radius": "10px"},
)

metrics = dbc.Row([
    dbc.Col(metric_1),
    dbc.Col(metric_2),
    dbc.Col(metric_3),
])

# Filters
# Extract all unique year-month values from the full dataset
all_months = df["year_month"].unique()
all_months_sorted = sorted(all_months)  # Ensure months are sorted

# Create a mapping of months to index positions for the slider
month_labels = {i: label for i, label in enumerate(all_months_sorted)}

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
            {"label": " Merchant", "value": "Merchant"}
        ],
        value="Amazon",  # Default selection
        inline=False,  # Ensure vertical stacking
        className="mt-2"
    )
], width=3)

# Checkbox for order status
status_checkbox = dbc.Col([
    dcc.Checklist(
        id="status-checkbox",
        options=[
            {"label": "Shipped", "value": "Shipped"},
            {"label": "Delivered to Buyer", "value": "Shipped - Delivered to Buyer"},
            {"label": "Picked Up", "value": "Shipped - Picked Up"},
            {"label": "Out for Delivery", "value": "Shipped - Out for Delivery"},
            {"label": "Cancelled", "value": "Cancelled"},
            {"label": "Returned to Seller", "value": "Shipped - Returned to Seller"},
            {"label": "Lost in Transit", "value": "Shipped - Lost in Transit"},
            {"label": "Pending", "value": "Pending"},
            {"label": "Shipping", "value": "Shipping"}
        ],
        value=["Shipped", "Shipped - Delivered to Buyer"],  # Default selection
        inline=False  # Display vertically
    )
])


# Filters section (moving slider under "Space for Filters")
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

            html.Label("Promotions Applied:", className="fw-bold mt-3", style={"color": "#34495e"}),
            dbc.Switch(id="promotion-toggle", value=False, className="ms-2"),
            html.Hr(),

            html.Label("Fulfillment Type:", className="fw-bold mt-3", style={"color": "#34495e"}),
            dbc.RadioItems(
                id="fulfillment-radio",
                options=[
                    {"label": " Amazon", "value": "Amazon"},
                    {"label": " Merchant", "value": "Merchant"}
                ],
                value="Amazon",
                inline=True,
                className="mt-2"
            ),
            html.Hr(),

            html.Label("Order Status:", className="fw-bold mt-3", style={"color": "#34495e"}),
            dbc.Checklist(
                id="status-checkbox",
                options=[{"label": x, "value": x} for x in df["Status"].unique()],
                inline=False,
                className="mt-2"
            )
        ]),
        className="shadow-sm rounded-3 p-4",
        style={"background-color": "#ffffff", "border": "1px solid #ddd", "width": "350px"}  # Reduced width
    )
], width="auto", className="d-flex justify-content-center")



# Charts
chart1 = None  # Placeholder for chart 1
chart2 = None  # Placeholder for chart 2

# Visuals
visuals = dbc.Row([
    dbc.Col(html.Div(), md=4),
    dbc.Col([
        dbc.Row(dcc.Graph(figure=fig)),
        dbc.Row([
            dbc.Col(html.Div("Chart 1 goes here")),
            dbc.Col(html.Div("Chart 2 goes here")),
        ]),
    ]),
])

# Layout
app.layout = dbc.Container([
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
    ], align="start", className="mb-4")
], fluid=True)





# Server side callbacks/reactivity
@app.callback(
    Output("filtered-data", "children"),  # Debugging output
    Output("filtered-df-store", "data"),  # Store filtered data for teammates
    Input("date-slider", "value"),
    Input("promotion-toggle", "value"),
    Input("fulfillment-radio", "value"),
    Input("status-checkbox", "value"),
)
def update_filtered_data(selected_index, promo_filter, fulfillment_filter, selected_statuses):
    # Convert slider index to corresponding year-month
    selected_date = month_labels.get(selected_index, None)

    if not selected_date:
        return "Invalid date selection.", dash.no_update

    # Filter dataset based on selected month
    filtered_df = df[df["year_month"] == selected_date]

    # Apply promotion filter
    if promo_filter:
        filtered_df = filtered_df[filtered_df["Promo"] > 0]  # Assuming "Promo" > 0 means applied

    # Apply fulfillment filter
    filtered_df = filtered_df[filtered_df["Fulfillment"] == fulfillment_filter]

    # Apply order status filter
    if selected_statuses:
        filtered_df = filtered_df[filtered_df["Status"].isin(selected_statuses)]

    # Store the filtered dataset as JSON (so teammates can use it)
    filtered_data_json = filtered_df.to_json(orient="split")

    return f"Filtered dataset contains {len(filtered_df)} records for {selected_date}.", filtered_data_json


# Run the app/dashboard
if __name__ == '__main__':
    app.run(debug=False)
    