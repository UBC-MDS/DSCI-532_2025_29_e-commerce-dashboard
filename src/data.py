import pandas as pd
import geopandas as gpd

# Import sales data for dashboard
def import_data(url):
    """
    Import and preprocess sales data from a CSV file.

    Args:
        url (str): URL or file path to the CSV file.

    Returns:
        pd.DataFrame: Preprocessed sales data.
    """
    df = pd.read_csv(url, nrows=None)
    # add a filterable date_value for the 1st of the month
    df['date_value'] = pd.to_datetime(df['year_month'] + '-01')
    return df

# Import geojson file for India
def import_geojson(url):
    """
    Import geojson data for India.

    Args:
        url (str): URL or file path to the geojson file.

    Returns:
        gpd.GeoDataFrame: GeoDataFrame containing geojson data for India.
    """
    india = gpd.read_file(url).query("iso_a2 == 'IN'")
    india.rename(columns={'name': 'state'}, inplace=True)

    return india

# Preprocess data
def preprocess_data(df):
    """
    Preprocess sales data to compute various metrics and mappings.

    Args:
        df (pd.DataFrame): Preprocessed sales data.

    Returns:
        dict: Dictionary containing computed metrics and mappings.
    """
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

    # Create a mapping of weeks
    weeks = df['year_week'].unique()
    sorted_weeks = sorted(weeks, key=lambda x: pd.to_datetime(x.split('/')[0]))
    week_labels = {i: week for i, week in enumerate(sorted_weeks)}

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

    return {
        "status_mapping": status_mapping,
        "month_labels": month_labels,
        "week_labels": week_labels,
        "total_revenue_current": total_revenue_current,
        "revenue_mom_change": revenue_mom_change,
        "total_quantity_current": total_quantity_current,
        "quantity_mom_change": quantity_mom_change,
        "completion_rate_current": completion_rate_current,
        "completion_rate_mom_change": completion_rate_mom_change
    }