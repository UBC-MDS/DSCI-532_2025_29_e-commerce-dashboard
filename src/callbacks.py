import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from dash import Input, Output, callback
from .app import df, month_labels, status_mapping, india

@callback(
    Output("filtered-data", "children"),  # Debugging output
    Output("filter_condition", "data"),
    Input("date-slider", "value"),
    Input("promotion-toggle", "value"),
    Input("fulfillment-radio", "value"),
    Input("status-checkbox", "value"),
    Input("map", "clickData"),
)
def update_filtered_data(selected_index, promo_filter, fulfillment_filter, selected_statuses, click_data):
    """
    Update the filtered data based on user inputs.

    Args:
        selected_index (int): Selected index from the date slider.
        promo_filter (bool): Promotion filter toggle value.
        fulfillment_filter (str): Selected fulfillment type.
        selected_statuses (list): List of selected order statuses.
        click_data (dict): Data from map click event.

    Returns:
        tuple: filtering message and filter condition.
    """
    # Convert slider index to corresponding year-month
    selected_date = month_labels.get(selected_index, None)

    if not selected_date:
        return "No selection", ""

    # set end date to proper date
    filter_end_date = pd.to_datetime(f'{selected_date}-01') + pd.DateOffset(months=1)
    filter_condition = f'(date_value < "{filter_end_date}")'

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

    return f"Showing {filtered_df['order_count'].sum():,.0f} records up to {selected_date}.", filter_condition

@callback(
    Output("map", "figure"),
    Input("filter_condition", "data"),
    Input("map", "clickData")  # Add clickData input to get the selected state
)
def create_map(query, click_data):
    """
    Create the map visualization based on the filtered data.

    Args:
        query (str): Filter condition query.
        click_data (dict): Data from map click event.

    Returns:
        plotly.graph_objects.Figure: Map figure.
    """
    states = df['state'].unique()

    # Remove the state filter condition from the query
    query_parts = query.split(' & ')
    query_parts = [part for part in query_parts if not part.startswith('(state ==')]
    modified_query = ' & '.join(query_parts)
    state_sales = df.query(modified_query).groupby('state')['Amount'].sum().reset_index()

    # Populate states with no data with 0
    all_states = pd.DataFrame({'state': states})
    state_sales = all_states.merge(state_sales, on='state', how='left').fillna(0)

    # Add a column to indicate whether the state is selected
    state_sales['selected'] = state_sales['state'].apply(lambda x: x == click_data['points'][0]['location'] if click_data and 'points' in click_data else False)

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

    # Highlight the selected state
    fig.update_traces(marker_line_width=state_sales['selected'].apply(lambda x: 3 if x else 0),
                      marker_line_color='white')

    fig.update_geos(
        fitbounds="locations",
        visible=False,
        projection_scale=5,  # Adjust this value to zoom in or out
        center={"lat": 20.5937, "lon": 78.9629}  # Center the map on India
    )
    fig.update_layout(
        coloraxis_showscale=False,
        modebar=dict(remove=['select', 'lasso2d']),
        margin={"r":0,"t":50,"l":0,"b":0}  # Adjust margins to make the map wider
    )

    return fig

@callback(
    Output("sales", "figure"),
    Input("filter_condition", "data")
    # prevent_initial_call=True
)
def create_sales_chart(query):
    """
    Create the sales chart based on the filtered data.

    Args:
        query (str): Filter condition query.

    Returns:
        plotly.graph_objects.Figure: Sales chart figure.
    """
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
    """
    Create the product chart based on the filtered data.

    Args:
        query (str): Filter condition query.

    Returns:
        plotly.graph_objects.Figure: Product chart figure.
    """
    try:
        pre_select = df.query(query).groupby('Category')['Amount'].sum().reset_index()

        # get the top 5, merge the rest to 'others'
        ordered_categories = pre_select.nlargest(5, ['Amount'], 'first')['Category'].tolist()  
        pre_select['Category'] = pre_select['Category'].apply(lambda x: x if x in ordered_categories else 'Others')      
        selection = pre_select.groupby('Category')['Amount'].sum().reset_index()

        # add 'Others' if in index (it is possible, some will have <5 categories)
        if ('Others' in selection['Category'].values):
            # append at end to ensure it is displayed last
            ordered_categories.append('Others')

        total_amount = selection['Amount'].sum()
        selection['Percentage'] = (selection['Amount'] / total_amount) * 100

        """
        product = px.pie(
            selection,
            values='Amount',
            names='Category',
            title='Product Categories',
            hover_data=['Amount', 'Percentage'],
            labels={'Amount': 'Total Amount', 'Percentage': 'Percentage'}
        )
        product.update_traces(textposition='inside', textinfo='percent+label')"
        """
        product = px.bar(selection, x = 'Amount', 
                         y = 'Category', color = 'Category', 
                         orientation='h',
                         hover_data=['Amount', 'Percentage'],
                         #height = 'auto'
                         )
        # hide legend and y-axis since Category names are specified
        product.update_layout(showlegend = False)
        product.update_layout(xaxis_title = 'Sales Amount', 
                              yaxis_title = None)
        # sort by totals
        #product.update_layout(yaxis={'categoryorder':'total ascending'})
        product.update_yaxes(categoryorder = 'array', 
                             categoryarray = ordered_categories[::-1])

        return product
    except Exception as e:
        print(f"Error in create_product_chart: {e}")
        return go.Figure(data=[go.Scatter(x=[], y=[], mode='text', text=f"Error: {e}")])