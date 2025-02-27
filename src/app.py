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
df = df[df["year_month"].isin(["2022-05", "2022-06"])]


# Compute Revenue Change (June vs May)
revenue_mom = df.groupby("year_month")["Amount"].sum()

# Ensure we have at least two months of data before computing the percentage change
if len(revenue_mom) > 1:
    revenue_mom_change = (revenue_mom.pct_change().iloc[-1]) * 100
else:
    revenue_mom_change = 0  # Default to 0% change if not enough data


# Compute Quantity Sold Change
qty_mom = df.groupby("year_month")["Qty"].sum()
# Ensure we have at least two months of data before computing the percentage change
if len(qty_mom) > 1:
    quantity_mom_change = (qty_mom.pct_change().iloc[-1]) * 100
else:
    quantity_mom_change = 0  # Default to 0% change if not enough data


total_revenue_june = revenue_mom["2022-06"]
total_quantity_june = qty_mom["2022-06"]

# Compute Completed Orders Percentage
completed_status = ["Shipped", "Shipped - Delivered to Buyer", "Shipped - Picked Up", "Shipped - Out for Delivery"]
df["order_status_category"] = df["Status"].apply(lambda x: "Completed" if x in completed_status else "Uncompleted")

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
filters = None  # Placeholder for filters

# Charts
chart1 = None  # Placeholder for chart 1
chart2 = None  # Placeholder for chart 2

# Visuals
visuals = dbc.Row([
    dbc.Col(html.Div("Space for Filters"), md=4),
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
    title,
    metrics,
    visuals
])

# Server side callbacks/reactivity
# ...

# Run the app/dashboard
if __name__ == '__main__':
    app.run(debug=False)
