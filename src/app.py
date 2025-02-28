from dash import Dash, html, dcc, Input, Output, callback
import dash_bootstrap_components as dbc
import dash_vega_components as dvc
import pandas as pd
import altair as alt
import geopandas as gpd

alt.data_transformers.enable('vegafusion')

def import_data():

    # Import and clean sales data
    df = pd.read_csv('data/raw/amazon_sample.zip')
    df = df.iloc[:, :-1]  # Drop last column
    df.rename(columns={'ship-state' : 'state'}, inplace=True)
    df['state'] = df['state'].str.title()
    df['state'].dropna(inplace=True)
    df["Date"] = pd.to_datetime(df["Date"], format="%m-%d-%y", errors="coerce")

    # Import geojson file for India
    url = 'https://naciscdn.org/naturalearth/50m/cultural/ne_50m_admin_1_states_provinces.zip'
    india = gpd.read_file(url).query("iso_a2 == 'IN'")
    india.rename(columns={'name' : 'state'}, inplace=True)

    # Mapping to rename state names in sales data
    state_mapping = {
        'Dadra And Nagar': 'Dadra and Nagar Haveli and Daman and Diu',
        'New Delhi': 'Delhi',
        'Andaman & Nicobar ': 'Andaman and Nicobar',
        'Jammu & Kashmir ': 'Jammu and Kashmir',
        'Rj': 'Rajasthan'
    }

    df['state'] = df['state'].replace(state_mapping)
    df.dropna(inplace=True)

    return df, india

# Initiatlize the app
app = Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])
server = app.server

# Data
df, india = import_data()

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

# Components
# Header / Title
title = dbc.Row(html.H1("Sales Dashboard"), id='title')

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
    dbc.Col(metric_3)
], id='metrics')

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
            {"label": " Merchant", "value": "Merchant"},
            {"label": " Both", "value": "Both"}  # New option added
        ],
        value="Both",  # Default selection to show all by default
        inline=False,
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
state_sales = df.groupby('state')['Amount'].sum().reset_index()
map = alt.Chart(india, width='container').mark_geoshape(stroke='grey').encode(
            color=alt.Color("Amount:Q", legend=None),
            tooltip=['state:N', 'Amount:Q']
        ).transform_lookup(
            lookup="state",
            from_=alt.LookupData(state_sales, "state", ["Amount"])
        ).add_params(
            alt.selection_point(fields=["state"], name="selected_states")
        ).to_dict(format='vega')

# Visuals
visuals = dbc.Row([
            dbc.Col(html.Div("Space for Filters"), md=4, id='filters'),
            dbc.Col([
                dbc.Row(dvc.Vega(id='map', spec=map, signalsToObserve=['selected_states'])),
                dbc.Row([
                    dbc.Col(dvc.Vega(id='sales', spec={})),
                    dbc.Col(dvc.Vega(id='product', spec={}))
                ]),
            ], 'charts'),
        ], id='visuals')

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
    Output("filtered-df", "data"),  # Store filtered data
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
    if fulfillment_filter != "Both":  # If not "Both", filter accordingly
        filtered_df = filtered_df[filtered_df["Fulfillment"] == fulfillment_filter]

    # Apply order status filter
    if selected_statuses:
        filtered_df = filtered_df[filtered_df["Status"].isin(selected_statuses)]

    return filtered_df

@callback(
    Output("sales", "spec"),
    Input("map", "signalData"),
    Input("filtered-df", "data")
    # prevent_initial_call=True
)
def create_sales_chart(signal_data, df):
    print(df.columns)
    if not signal_data or not signal_data['selected_states']:
        # If no state selected, use the entire data set
        selection = df
    else:
        state = signal_data['selected_states']['state'][0]
        selection = df[df['state'] == state]

    sales = alt.Chart(selection, width='container').mark_line().encode(
                x=alt.X('yearmonth(Date):T', title='Month'),
                y=alt.Y('sum(Amount):Q', title='Total Amount')
            ).to_dict(format='vega')

    return sales

@callback(
    Output("product", "spec"),
    Input("map", "signalData"),
    # prevent_initial_call=True
)
def create_product_chart(signal_data):
    if not signal_data or not signal_data['selected_states']:
        # If no state selected, use the entire data set
        selection = df.groupby('Category')['Amount'].sum().reset_index()
    else:
        state = signal_data['selected_states']['state'][0]
        selection = df[df['state'] == state].groupby('Category')['Amount'].sum().reset_index()
    
    product = alt.Chart(selection, width='container').mark_arc(innerRadius=50).encode(
                theta="Amount",
                color="Category:N",
            ).to_dict(format='vega')

    return product

# Run the app/dashboard
if __name__ == '__main__':
    app.run(debug=True)