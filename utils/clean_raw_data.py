"""
This script pre-processes the original raw file from Kaggle and prepares it to be used
in the dashboard. It is not part of the Dash dashboard files
"""

import pandas as pd
import os

# read the raw zipped data that was downloaded from Kaggle
data_path = 'data/raw/'
file_path = os.path.join(data_path, 'Amazon_Sale_Report.zip')

df = pd.read_csv(file_path, index_col = 0, dtype = {23: str})
df['Date'] = pd.to_datetime(df['Date'], format = '%m-%d-%y')

df = df.iloc[:, :-1]  # Drop last column, not required

# create some derived columns
df['is_promotion'] = df['promotion-ids'].notna() # will capture both NA and empty string
df['year_month'] = df["Date"].dt.to_period("M").astype(str) # the month from date
df['year_week'] = df["Date"].dt.to_period("W").astype(str) # the week from date

# pre-process the geolocation, state
df.rename(columns={'ship-state': 'state'}, inplace=True)
df['state'] = df['state'].str.title()
df['state'].dropna(inplace=True)

# Mapping to rename/clean state names in sales data
state_mapping = {
    'Dadra And Nagar': 'Dadra and Nagar Haveli and Daman and Diu',
    'New Delhi': 'Delhi',
    'Andaman & Nicobar ': 'Andaman and Nicobar',
    'Jammu & Kashmir ': 'Jammu and Kashmir',
    'Rj': 'Rajasthan'
}

df['state'] = df['state'].replace(state_mapping)

# summarize the data by grouping along the dimensions that will be queried/filtered
sample_df = df.groupby(['year_month', 'year_week', 
            'Status', 'Fulfilment', 'Category', 
            'state', 'is_promotion',]).agg(
                # and aggregate the metrics that will be shown
                {'Qty': 'sum', 'Order ID': 'size', 'Amount': 'sum'}
                ).reset_index().sample(frac=0.5, 
                                       replace=False, 
                                       random_state=532)

# rename Order ID summary as order_count
sample_df.rename(columns={'Order ID': 'order_count'}, inplace=True)

# output data
output_path = 'data'
output_file = 'amazon_sample'
compression_options = dict(method='zip', archive_name=f'{output_file}.csv')
sample_df.to_csv(os.path.join(output_path, f'{output_file}.zip'), 
                 compression = compression_options)