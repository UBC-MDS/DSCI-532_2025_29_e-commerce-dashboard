from dash import Dash, html, dcc, Input, Output, callback
import dash_bootstrap_components as dbc
import dash_vega_components as dvc
import pandas as pd
import altair as alt
import geopandas as gpd

alt.data_transformers.enable('vegafusion')

# Import sales data for dashboard
def import_data():

    # Import and clean sales data
    df = pd.read_csv('data/raw/amazon_sample.zip')

    # Drop last column
    df = df.iloc[:, :-1]  # Drop last column

    # Rename column name and drop na valuesconda 
    df.rename(columns={'ship-state' : 'state'}, inplace=True)
    df['state'] = df['state'].str.title()
    df['state'].dropna(inplace=True)

    # Convert Date column to datetime
    df["Date"] = pd.to_datetime(df["Date"], format="%m-%d-%y", errors="coerce")

    # Extract year-month for aggregation
    df["year_month"] = df["Date"].dt.to_period("M").astype(str)

    # Ddd flag for promotions
    df['is_promotion'] = df['promotion-ids'].notna() # will capture both NA and empty string

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
    india.rename(columns={'name' : 'state'}, inplace=True)

    return india

# Function to format numeric values
def format_large_num(value):
    value = float('{:.3g}'.format(value))
    magnitude = 0
    while abs(value) >= 1000:
        magnitude += 1
        value /= 1000.0
    return '{}{}'.format('{:f}'.format(value).rstrip('0').rstrip('.'), ['', 'K', 'M', 'B', 'T'][magnitude])

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
if len(completion_rate.index)>1:
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
        options=[key for key, _ in status_mapping.items() ],
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
                options=[key for key, _ in status_mapping.items() ],
                inline=False,
                className="mt-2"
            ),
            html.Br(),

            html.Div(id = "filtered-data", style={"font-size": "8px", "font-style": "italic"})
        ]),
        className="shadow-sm rounded-3 p-4",
        style={"background-color": "#ffffff", "border": "1px solid #ddd", "width": "350px"}  # Reduced width
    )
], width="auto", className="d-flex justify-content-center")

# Charts
state_sales = df.groupby('state')['Amount'].sum().reset_index()
map = alt.Chart(india, width='container', title="Sales by State and Territories").mark_geoshape(stroke='grey').encode(
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
    ], align="start", className="mb-4")
], fluid=True)

# Server side callbacks/reactivity
@app.callback(
    [Output("filtered-data", "children"),  # Debugging output
    Output("filter_condition", "data")],
    [Input("date-slider", "value"),
    Input("promotion-toggle", "value"),
    Input("fulfillment-radio", "value"),
    Input("status-checkbox", "value"),
    Input("map", "signalData")]
)
def update_filtered_data(selected_index, promo_filter, fulfillment_filter, selected_statuses, signal_data):
    print(f'signal_data is {signal_data}')
    # Convert slider index to corresponding year-month
    selected_date = month_labels.get(selected_index, None)

    if not selected_date:
        return "No selection"

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

    if signal_data and 'state' in signal_data['selected_states']:
        state = signal_data['selected_states']['state'][0]
        filter_condition += f' & (state == "{state}")'

    # Store the filtered dataset
    print(f'query is {filter_condition}')
    filtered_df = df.query(filter_condition)
    print(f'query columns are {filtered_df.columns}')

    return f"Showing {len(filtered_df):,.0f} records up to {selected_date}.", filter_condition

@app.callback(
    Output("sales", "spec"),
    Input("filter_condition", "data")
)
def create_sales_chart(query):
    print('Creating sales chart')
    selection = df.query(query)
    selection = df
    sales = alt.Chart(selection, width='container', title="Monthly Sales"
                      ).mark_line().encode(
                        x=alt.X('yearmonth(Date):T', title='Month'),
                        y=alt.Y('sum(Amount):Q', title='Total Amount')
                    ).to_dict(format='vega')

    return sales

@app.callback(
    Output("product", "spec"),
    Input("filter_condition", "data")
    # prevent_initial_call=True
)
def create_product_chart(query):
    selection = df.query(query)
    selection = selection.groupby('Category')['Amount'].sum().reset_index()
    
    product = alt.Chart(selection, width='container', title="Product Categories"
                        ).mark_arc(innerRadius=50).encode(
                            theta="Amount",
                            color=alt.Color(field="Category", type="nominal", legend=alt.Legend(title=None)),
                        ).to_dict(format='vega')

    return product

# Run the app/dashboard
if __name__ == '__main__':
    app.run(debug=False)