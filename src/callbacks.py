import pandas as pd
from dash import html
import plotly.express as px
import plotly.graph_objects as go
import dash_bootstrap_components as dbc
from dash import Input, Output, callback
from .app import df, month_labels, week_labels, status_mapping, india
from .components import format_large_num

@callback(
    Output("filtered-data", "children"),  # Debugging output
    Output("filter_condition", "data"),
    Input("date-slider", "value"),       # Monthly slider value
    Input("week-range-slider", "value"), # Week range slider value [start, end]
    Input("promotion-toggle", "value"),
    Input("fulfillment-radio", "value"),
    Input("status-checkbox", "value"),
    Input("map", "clickData"),
    Input("time_granularity", "value")   # Radio button for Monthly/Weekly
)
def update_filtered_data(date_slider_value, week_range_value, promo_filter, fulfillment_filter, selected_statuses, click_data, time_granularity):
    """
    Update the filtered data based on user inputs.

    Args:
        date_slider_value (int): Selected index from the date slider.
        week_range_value (list): Selected [start, end] week indices from the range slider.
        promo_filter (bool): Promotion filter toggle value.
        fulfillment_filter (str): Selected fulfillment type.
        selected_statuses (list): List of selected order statuses.
        click_data (dict): Data from map click event.
        time_granularity (str): "Monthly" or "Weekly" - determines if filtering is based on months or weeks.

    Returns:
        tuple: filtering message and filter condition.
    """
    if time_granularity == "Monthly":
        selected_index = date_slider_value
        selected_date = month_labels.get(selected_index, None)
        if not selected_date:
            return "No selection", ""
        filter_end_date = pd.to_datetime(f'{selected_date}-01') + pd.DateOffset(months=1)
        filter_condition = f'(date_value < "{filter_end_date}")'
        display_date = selected_date
    else:  # Weekly
        start_index, end_index = week_range_value  #Unpack the range slider values
        print(f"start_index: {start_index}, end_index: {end_index}")

        all_weeks = list(week_labels.values())  # example -  ['2022-03-28/2022-04-03', '2022-04-04/2022-04-10']
        selected_weeks = all_weeks[start_index:end_index + 1]
        
        start_week = week_labels.get(start_index, None)
        end_week = week_labels.get(end_index, None)
        print(f"start_week: {start_week}, end_week: {end_week}")
        
        if not start_week or not end_week:
            return "No selection", ""
        
        # Filter condition using the list of selected weeks
        filter_condition = f'(year_week in {selected_weeks})'
        display_date = f"{start_week[-5:]}-{end_week[-5:]}"

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

    return f"Showing {filtered_df['order_count'].sum():,.0f} records for {display_date}.", filter_condition

@callback(
    Output("metric-1", "children"),  # Revenue metric
    Output("metric-2", "children"),  # Quantity metric
    Output("metric-3", "children"),  # Completion rate metric
    Input("date-slider", "value"),
    Input("promotion-toggle", "value"),
    Input("fulfillment-radio", "value"),
    Input("status-checkbox", "value"),
    Input("map", "clickData"),
)
def update_metrics(selected_index, promo_filter, fulfillment_filter, selected_statuses, click_data):
    """
    Update the metric cards dynamically based on all filters.

    Args:
        selected_index (int): Selected index from the date slider.
        promo_filter (bool): Whether promotion filter is applied.
        fulfillment_filter (str): Selected fulfillment type.
        selected_statuses (list): List of selected order statuses.
        click_data (dict): Data from map click event.

    Returns:
        tuple: Updated metric contents for revenue, quantity, and completion rate.
    """
    # Convert slider index to corresponding year-month
    selected_date = month_labels.get(selected_index, None)

    if not selected_date:
        return dbc.CardBody("N/A"), dbc.CardBody("N/A"), dbc.CardBody("N/A")

    selected_month = pd.to_datetime(f"{selected_date}-01")
    previous_month = selected_month - pd.DateOffset(months=1)
    previous_month_str = previous_month.strftime("%Y-%m")

    # Apply filters to dataset
    filter_condition = f'year_month == "{selected_date}"'

    if promo_filter:
        filter_condition += ' & (is_promotion == True)'

    if fulfillment_filter != "Both":
        filter_condition += f' & (Fulfilment == "{fulfillment_filter}")'

    if selected_statuses:
        filter_statuses = [item for key, values in status_mapping.items() for item in values if key in selected_statuses]
        filter_statuses_str = ', '.join([f'"{status}"' for status in filter_statuses])
        filter_condition += f' & (Status in [{filter_statuses_str}])'

    if click_data and 'points' in click_data:
        state = click_data['points'][0]['location']
        filter_condition += f' & (state == "{state}")'

    # Filter dataset for the selected month
    filtered_df = df.query(filter_condition)

    # Compute revenue, quantity, and completion rate for selected month
    revenue_selected = filtered_df["Amount"].sum()
    quantity_selected = filtered_df["Qty"].sum()

    completed_status = ["Shipped", "Shipped - Delivered to Buyer", "Shipped - Picked Up", "Shipped - Out for Delivery"]
    completed_orders = filtered_df[filtered_df["Status"].isin(completed_status)]
    completion_rate_selected = (len(completed_orders) / len(filtered_df)) * 100 if len(filtered_df) > 0 else 0

    # Compute the previous month's metrics
    if previous_month_str in df["year_month"].unique():
        prev_df = df.query(f'year_month == "{previous_month_str}"')

        if promo_filter:
            prev_df = prev_df[prev_df["is_promotion"] == True]

        if fulfillment_filter != "Both":
            prev_df = prev_df[prev_df["Fulfilment"] == fulfillment_filter]

        if selected_statuses:
            prev_df = prev_df[prev_df["Status"].isin(filter_statuses)]

        if click_data and 'points' in click_data:
            prev_df = prev_df[prev_df["state"] == state]

        revenue_prev = prev_df["Amount"].sum()
        quantity_prev = prev_df["Qty"].sum()
        completed_prev = prev_df[prev_df["Status"].isin(completed_status)]
        completion_rate_prev = (len(completed_prev) / len(prev_df)) * 100 if len(prev_df) > 0 else 0

        revenue_mom_change = ((revenue_selected - revenue_prev) / revenue_prev) * 100 if revenue_prev > 0 else 0
        quantity_mom_change = ((quantity_selected - quantity_prev) / quantity_prev) * 100 if quantity_prev > 0 else 0
        completion_rate_mom_change = ((completion_rate_selected - completion_rate_prev) / completion_rate_prev) * 100 if completion_rate_prev > 0 else 0
    else:
        revenue_mom_change = 0
        quantity_mom_change = 0
        completion_rate_mom_change = 0

    # **Set color and arrow indicators**
    def format_mom_change(value):
        abs_value = abs(value)  # Get the absolute value (remove sign)
        if value > 0:
            return html.Span([f"{abs_value:.1f}% ", "▲ ", " past month"], style={"color": "orange", "font-weight": "bold"})
        elif value < 0:
            return html.Span([f"{abs_value:.1f}% ", "▼ ", " past month"], style={"color": "skyblue", "font-weight": "bold"})
        else:
            return html.Span([f"{abs_value:.1f}% ", " past month"], style={"color": "gray", "font-weight": "bold"})


    # **Wrap metrics inside dbc.CardBody()**
    metric_1_content = dbc.CardBody([
        html.H3("Revenue", className="card-title", style={"font-size": "18px", "color": "#2c3e50"}),
        html.H1(f"₹{revenue_selected:,.2f}", className="card-text", style={"font-size": "30px", "font-weight": "bold", "color": "#000"}),
        html.Small(format_mom_change(revenue_mom_change), className="card-text text-muted", style={"font-size": "14px"})
    ])

    metric_2_content = dbc.CardBody([
        html.H3("Quantity Sold", className="card-title", style={"font-size": "18px", "color": "#2c3e50"}),
        html.H1(f"{quantity_selected:,.0f}", className="card-text", style={"font-size": "30px", "font-weight": "bold", "color": "#000"}),
        html.Small(format_mom_change(quantity_mom_change), className="card-text text-muted", style={"font-size": "14px"})
    ])

    metric_3_content = dbc.CardBody([
        html.H3("Completed Orders", className="card-title", style={"font-size": "18px", "color": "#2c3e50"}),
        html.H1(f"{completion_rate_selected:.2f}%", className="card-text", style={"font-size": "30px", "font-weight": "bold", "color": "#000"}),
        html.Small(format_mom_change(completion_rate_mom_change), className="card-text text-muted", style={"font-size": "14px"})
    ])

    return metric_1_content, metric_2_content, metric_3_content

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
    state_sales.rename(columns={'state' : 'State'}, inplace=True)

    fig = px.choropleth(
        state_sales,
        geojson=india.__geo_interface__,
        locations='State',
        featureidkey="properties.state",
        color='Amount',
        hover_name='State',
        hover_data={'State': True},
        color_continuous_scale=px.colors.sequential.Bluyl
    )

    # Custom hover template
    fig.update_traces(
        hovertemplate="<b>%{hovertext}</b>",
        hovertext=state_sales['State'] + '<br>Amount: ₹' + state_sales['Amount'].apply(lambda x: f'{x/1e6:.1f}M' if x >= 1e6 else f'{x/1e3:.1f}K' if x >= 1e3 else f'{x:.0f}')
    )

    # Highlight the selected state
    fig.update_traces(marker_line_width=state_sales['selected'].apply(lambda x: 3 if x else 1),
                      marker_line_color='black')

    fig.update_geos(
        fitbounds="locations",
        visible=False,
        projection_type="mercator",
        projection_scale=6,  # Adjust this value to zoom in or out
        center={"lat": 20.5937, "lon": 78.9629}  # Center the map on India
    )
    fig.update_layout(
        modebar=dict(remove=['select', 'lasso2d']),
        margin={"r":0,"t":50,"l":0,"b":0},
        coloraxis_colorbar=dict(
            x=-0.1,  # Move color scale to the left
            title="Sales",
            ticks="outside"
        )
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

@callback(
    Output('date-slider-container', 'style'),
    Output('week-selector-container', 'style'),
    Output('month-label', 'style'),
    Output('week-label', 'style'),
    Input('time_granularity', 'value')
)
def toggle_time_selection_visibility(time_granularity):
    """
    Toggle visibility of monthly slider and weekly dropdown based on time granularity selection.
    
    Args:
        time_granularity (str): Selected value from the radio buttons ('Monthly' or 'Weekly')
    
    Returns:
        tuple: Styles for date slider container, week selector container, month label, and week label
    """
    if time_granularity == 'Monthly':
        return (
            {'display': 'block'},  # Show monthly slider
            {'display': 'none'},   # Hide weekly dropdown
            {'display': 'block', 'color': '#34495e', 'font-weight': 'bold'},  # Show month label
            {'display': 'none'}    # Hide week label
        )
    else:  # Weekly
        return (
            {'display': 'none'},   # Hide monthly slider
            {'display': 'block'},  # Show weekly dropdown
            {'display': 'none'},   # Hide month label
            {'display': 'block', 'color': '#34495e', 'font-weight': 'bold'}  # Show week label
        )