import pandas as pd
from dash import html
import plotly.express as px
import plotly.graph_objects as go
import dash_bootstrap_components as dbc
from dash import Input, Output, callback
from .app import df, month_labels, week_labels, status_mapping, india, cache
from .components import format_large_num, format_indian_rupees

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
        start_index, end_index = date_slider_value  # Now using a range
        all_months = list(month_labels.values())

        if start_index is None or end_index is None or start_index < 0 or end_index >= len(all_months):
            return "No selection", ""

        selected_months = all_months[start_index:end_index + 1]  # Get range
        filter_condition = f'(year_month in {selected_months})'
        display_date = f"{selected_months[0]} to {selected_months[-1]}"

    else:  # Weekly
        start_index, end_index = week_range_value  #Unpack the range slider values

        all_weeks = list(week_labels.values())  # example -  ['2022-03-28/2022-04-03', '2022-04-04/2022-04-10']
        selected_weeks = all_weeks[start_index:end_index + 1]
        
        start_week = week_labels.get(start_index, None)
        end_week = week_labels.get(end_index, None)
        
        if not start_week or not end_week:
            return "No selection", ""
        
        # Filter condition using the list of selected weeks
        filter_condition = f'(year_week in {selected_weeks})'
        display_date = f"{start_week[:10]} to {end_week[-10:]}"
        #print(f"Start {start_week} to {end_week}")

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
    Input("date-slider", "value"),       # Monthly slider value
    Input("week-range-slider", "value"), # Week range slider value [start, end]
    Input("promotion-toggle", "value"),
    Input("fulfillment-radio", "value"),
    Input("status-checkbox", "value"),
    Input("map", "clickData"),
    Input("time_granularity", "value")  # Radio button for Monthly/Weekly
)
def update_metrics(date_slider_value, week_range_value, promo_filter, fulfillment_filter, selected_statuses, click_data, time_granularity):
    """
    Update the metric cards dynamically based on all filters.

    Returns:
        tuple: Updated metric contents for revenue, quantity, and completion rate.
    """
    if time_granularity == "Monthly":
        start_index, end_index = date_slider_value  # Now using a range
        all_months = list(month_labels.values())

        if start_index is None or end_index is None or start_index < 0 or end_index >= len(all_months):
            return dbc.CardBody("N/A"), dbc.CardBody("N/A"), dbc.CardBody("N/A")

        selected_months = all_months[start_index:end_index + 1]  # Get range
        filter_condition = f'(year_month in {selected_months})'
        period_type = "month"

    else:  # Weekly
        start_index, end_index = week_range_value
        all_weeks = list(week_labels.values())
        selected_weeks = all_weeks[start_index:end_index + 1]

        start_week = week_labels.get(start_index, None)
        end_week = week_labels.get(end_index, None)
        if not start_week or not end_week:
            return dbc.CardBody("N/A"), dbc.CardBody("N/A"), dbc.CardBody("N/A")

        filter_condition = f'(year_week in {selected_weeks})'
        period_type = "week"

    # Apply additional filters
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

    # Filter dataset for the selected period
    filtered_df = df.query(filter_condition)

    # Compute revenue, quantity, and completion rate
    revenue_selected = filtered_df["Amount"].sum()
    quantity_selected = filtered_df["Qty"].sum()

    completed_status = ["Shipped", "Shipped - Delivered to Buyer", "Shipped - Picked Up", "Shipped - Out for Delivery"]
    completed_orders = filtered_df[filtered_df["Status"].isin(completed_status)]
    completion_rate_selected = (len(completed_orders) / len(filtered_df)) * 100 if len(filtered_df) > 0 else 0

    def calculate_cagr(begin, end, time_years):
        """Calculate the Compound Annual Growth Rate (CAGR)."""
        if begin == 0:
            return None  # Prevent division by zero
        if time_years > 0:
            return ((end / begin) ** (1 / time_years) - 1) * 100
        return 0  # Default if time period is invalid

    # Extract the first and last period for CAGR calculation
    if time_granularity == "Monthly":
        start_index, end_index = date_slider_value
        all_months = list(month_labels.values())

        # Ensure indices are valid
        if start_index is None or end_index is None or start_index < 0 or end_index >= len(all_months):
            return dbc.CardBody("N/A"), dbc.CardBody("N/A"), dbc.CardBody("N/A")

        selected_months = all_months[start_index:end_index + 1]  # Get all months in range

        # First and last months in the selected range
        # Apply the same filters to the dataset before calculating CAGR
        filtered_df_cagr = df.query(filter_condition)

        revenue_begin = filtered_df_cagr[filtered_df_cagr["year_month"] == selected_months[0]]["Amount"].sum()
        revenue_end = filtered_df_cagr[filtered_df_cagr["year_month"] == selected_months[-1]]["Amount"].sum()


        quantity_begin = filtered_df_cagr[filtered_df_cagr["year_month"] == selected_months[0]]["Qty"].sum()
        quantity_end = filtered_df_cagr[filtered_df_cagr["year_month"] == selected_months[-1]]["Qty"].sum()

        completed_begin = filtered_df_cagr[
            (filtered_df_cagr["year_month"] == selected_months[0]) & 
            (filtered_df_cagr["Status"].isin(completed_status))
        ]
        completed_end = filtered_df_cagr[
            (filtered_df_cagr["year_month"] == selected_months[-1]) & 
            (filtered_df_cagr["Status"].isin(completed_status))
        ]
        total_orders_begin = filtered_df_cagr[filtered_df_cagr["year_month"] == selected_months[0]]["Status"].count()
        total_orders_end = filtered_df_cagr[filtered_df_cagr["year_month"] == selected_months[-1]]["Status"].count()



    elif time_granularity == "Weekly":
        filtered_df_cagr = df.query(filter_condition)

        revenue_begin = filtered_df_cagr[filtered_df_cagr["year_week"] == selected_weeks[0]]["Amount"].sum()
        revenue_end = filtered_df_cagr[filtered_df_cagr["year_week"] == selected_weeks[-1]]["Amount"].sum()

        quantity_begin = filtered_df_cagr[filtered_df_cagr["year_week"] == selected_weeks[0]]["Qty"].sum()
        quantity_end = filtered_df_cagr[filtered_df_cagr["year_week"] == selected_weeks[-1]]["Qty"].sum()

        completed_begin = filtered_df_cagr[(df["year_week"] == selected_weeks[0]) & filtered_df_cagr["Status"].isin(completed_status)]
        completed_end = filtered_df_cagr[(df["year_week"] == selected_weeks[-1]) & filtered_df_cagr["Status"].isin(completed_status)]

        total_orders_begin = filtered_df_cagr[filtered_df_cagr["year_week"] == selected_weeks[0]]["Status"].count()
        total_orders_end = filtered_df_cagr[filtered_df_cagr["year_week"] == selected_weeks[-1]]["Status"].count()

    # Convert selected range to years
    time_years = (end_index - start_index + 1) / 12 if time_granularity == "Monthly" else (end_index - start_index + 1) / 52

    # Compute CAGR for each metric
    revenue_cagr = calculate_cagr(revenue_begin, revenue_end, time_years)
    quantity_cagr = calculate_cagr(quantity_begin, quantity_end, time_years)

    # Compute Completion Rate Growth
    completion_rate_begin = (len(completed_begin) / total_orders_begin) * 100 if total_orders_begin > 0 else 0
    completion_rate_end = (len(completed_end) / total_orders_end) * 100 if total_orders_end > 0 else 0
    completion_rate_cagr = calculate_cagr(completion_rate_begin, completion_rate_end, time_years)

    # Set color and arrow indicators
    def format_cagr_change(value):
        """Format CAGR percentage with appropriate color and icon."""
        if value is None:
            return html.Span(["N/A"], style={"color": "gray", "font-weight": "bold"})
        abs_value = abs(value)
        if value > 0:
            return html.Span([f"{abs_value:.1f}% ", "▲ ", "Growth Rate"], style={"color": "orange", "font-weight": "bold"})
        elif value < 0:
            return html.Span([f"{abs_value:.1f}% ", "▼ ", "Growth Rate"], style={"color": "skyblue", "font-weight": "bold"})
        else:
            return html.Span(["No Growth"], style={"color": "gray", "font-weight": "bold"})

    # Wrap metrics inside dbc.CardBody()
    metric_1_content = dbc.CardBody([
        html.Label("Revenue", className="card-title", style={"fontsize":"20px"}),
        html.H4(format_indian_rupees(revenue_selected), className="card-text"),
        html.Small(format_cagr_change(revenue_cagr), className="card-text text-muted")
    ], style={"margin": "1px", "padding": "1px"})

    metric_2_content = dbc.CardBody([
        html.Label("Quantity Sold", className="card-title", style={"fontsize":"20px"}),
        html.H4(f"{quantity_selected:,.0f}", className="card-text"),
        html.Small(format_cagr_change(quantity_cagr), className="card-text text-muted")
    ], style={"margin": "1px", "padding": "1px"})

    metric_3_content = dbc.CardBody([
        html.Label("Completed Orders", className="card-title", style={"fontsize":"20px"}),
        html.H4(f"{completion_rate_selected:.2f}%", className="card-text"),
        html.Small(format_cagr_change(completion_rate_cagr), className="card-text text-muted")
    ], style={"margin": "1px", "padding": "1px"})

    return metric_1_content, metric_2_content, metric_3_content


@cache.memoize()
@callback(
    Output("map", "figure"),
    Output("state_summary", "figure"),
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
        plotly.graph_objects.Figure: Bar chart with per-state sales summary
    """
    states = df['state'].unique()

    # Remove the state filter condition from the query
    query_parts = query.split(' & ')
    query_parts = [part for part in query_parts if not part.startswith('(state ==')]
    modified_query = ' & '.join(query_parts)
    state_sales = df.query(modified_query).groupby('state')['Amount'].sum().reset_index()
    
    if state_sales.empty:
        fig = go.Figure()
        fig.add_annotation(
            text="No sales data available for the selected state.",
            x=0.5, y=0.5,
            xref="paper", yref="paper",
            showarrow=False,
            font=dict(size=16)
        )
        fig.update_layout(
            xaxis=dict(visible=False),
            yaxis=dict(visible=False),
            template="plotly_white"
        )
        
        # Also return an empty state summary figure
        state_summary = go.Figure()
        state_summary.add_annotation(
            text="No state-wise sales data available.",
            x=0.5, y=0.5,
            xref="paper", yref="paper",
            showarrow=False,
            font=dict(size=16)
        )
        state_summary.update_layout(
            xaxis=dict(visible=False),
            yaxis=dict(visible=False),
            template="plotly_white"
        )
        
        return fig, state_summary


    # Populate states with no data with 0
    all_states = pd.DataFrame({'state': states})
    state_sales = all_states.merge(state_sales, on='state', how='left').fillna(0)

    # Add a column to indicate whether the state is selected
    state_sales['selected'] = False
    if click_data and 'points' in click_data:
        state_sales.loc[state_sales['state'] == click_data['points'][0]['location'], 'selected'] = True
    state_sales.rename(columns={'state' : 'State'}, inplace=True)

    fig = px.choropleth(
        state_sales,
        geojson=india.__geo_interface__,
        locations='State',
        featureidkey="properties.state",
        color='Amount',
        hover_name='State',
        hover_data={'State': True},
        #color_continuous_scale=px.colors.sequential.Bluyl
    )

    # Custom hover template
    fig.update_traces(
        hovertemplate="%{hovertext}",
        hovertext=state_sales.apply(lambda row: f"{row['State']}<br>Amount: {format_indian_rupees(round(row['Amount']))}", axis=1),
    )

    # Highlight the selected state
    marker_line_width = state_sales['selected'].map({True: 3, False: 1})
    fig.update_traces(marker_line_width=marker_line_width,
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
        margin={"r":0,"t":20,"l":0,"b":0},
        dragmode=False,
        clickmode='event',
        hoverdistance=5,
        coloraxis_colorbar=dict(
            x=-0.1,
            y=0.5,
            title="Sales",
            ticks="outside"
        )
    )

    selected_state_names = state_sales[state_sales['selected']]['State'].tolist() 
    # set a color scale to be shared
    color_min = state_sales["Amount"].min()
    color_max = state_sales["Amount"].max()
    shared_color_axis = dict(colorscale="Bluyl", cmin=color_min, cmax=color_max)
    fig.update_layout(coloraxis = shared_color_axis)
    pre_select = state_sales.groupby('State')['Amount'].sum().reset_index()

    # 3 scenarios: 
    # a. <7 selected (select top 7 - selected)
    # b. >7 selected ( empty top 7, select top 7 from selected states)
    MAX_TOP_STATES = 7
    if (len(selected_state_names)<MAX_TOP_STATES):
        topn = MAX_TOP_STATES - len(selected_state_names)
        ordered_states = pre_select.nlargest(topn, ['Amount'], 'first')['State'].tolist() 
        # ensure selected states are shown, but only if not already included
        missing_selected = set(selected_state_names).difference(set(ordered_states))
        if len(missing_selected) > 0:
            ordered_states += list(selected_state_names)
    else:
        topn = MAX_TOP_STATES
        # select top MAX_TOP_STATES from among the selected states
        ordered_states = (
            pre_select[pre_select['State'].isin(selected_state_names)].nlargest(
                topn, ['Amount'], 'first'
                )['State'].tolist() 
        )
    #print('Selected:',  selected_state_names) 
    #print('Top:',  ordered_states) 

    # Replace apply with vectorized operation
    pre_select['State'] = pre_select['State'].map(lambda x: x if x in ordered_states else 'Others')      
    summary_selection = pre_select.groupby('State')['Amount'].sum().reset_index()
    

    # add 'Others' if in index
    if ('Others' in summary_selection['State'].values):
        # append at end to ensure it is displayed last
        ordered_states.append('Others')

    total_amount = summary_selection['Amount'].sum()
    summary_selection['Percentage'] = (summary_selection['Amount'] / total_amount)
    summary_selection['Sales Amount'] = summary_selection['Amount'].map(format_large_num)
    
    # summarized bar chart
    summary_bar = px.bar(summary_selection, x = 'Amount', 
                         y = 'State', color = 'Amount', 
                         orientation='h',
                         hover_data={'Sales Amount': True, 
                                     'Amount': False,
                                     'Percentage': ':.1%'}, 
                         #color_continuous_scale=px.colors.sequential.Bluyl                        
                         )
    # TODO: manually adjust the color for "Others", if present
    summary_bar.update_layout(coloraxis = shared_color_axis)

    # y-axis since state names are specified
    summary_bar.update_layout(xaxis_title = 'Sales Amount', 
                            yaxis_title = None)
    # sort by totals
    summary_bar.update_yaxes(categoryorder = 'array', 
                            categoryarray = ordered_states[::-1])
    # hide legend and color axis
    summary_bar.update_layout(showlegend = False, 
                              margin={"r":0,"t":30,"l":0,"b":0})
    summary_bar.update_coloraxes(showscale=False)

    return fig, summary_bar

@cache.memoize()
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
        # Apply the filter condition to the DataFrame
        selection = df.query(query)
        if selection.empty:
            fig = go.Figure()
            fig.add_annotation(
                text="No sales data available for the selected filters.",
                x=0.5, y=0.5,
                xref="paper", yref="paper",
                showarrow=False,
                font=dict(size=16)
            )
            fig.update_layout(
                xaxis=dict(visible=False),
                yaxis=dict(visible=False),
                template="plotly_white"
            )
            return fig

        # Determine if the filter is weekly or monthly based on the query content
        # If 'year_week' is in the query, assume weekly; otherwise, assume monthly
        if 'year_week' in query:
            # Group by year_week and sum the Amount
            selection = selection.groupby('year_week')['Amount'].sum().reset_index()
            
            # For plotting, use the start date of the week range as the x-axis value
            selection['plot_date'] = selection['year_week'].str.split('/').str[0]
            selection['plot_date'] = pd.to_datetime(selection['plot_date'])
            
            x_column = 'plot_date'
            x_label = 'Week Start'
        else:
            # Group by year_month and sum the Amount
            selection = selection.groupby('year_month')['Amount'].sum().reset_index()
            selection['year_month'] = pd.to_datetime(selection['year_month'])
            
            x_column = 'year_month'
            x_label = 'Month'

        # Create the line chart
        sales = px.line(
            selection,
            x=x_column,
            y='Amount',
            labels={x_column: x_label, 'Amount': 'Total Sales'},
            line_shape='linear'
        )

        # Disable pan and zoom
        sales.update_layout(
            xaxis=dict(fixedrange=True),
            yaxis=dict(fixedrange=True),
            margin={"r":0,"t":30,"l":0,"b":0},
        )

        return sales
    except Exception as e:
        print(f"Error in create_sales_chart: {e}")
        return go.Figure(data=[go.Scatter(x=[], y=[], mode='text', text=f"Error: {e}")])

@cache.memoize()
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
        if pre_select.empty:
            fig = go.Figure()
            fig.add_annotation(
                text="No product sales data available.",
                x=0.5, y=0.5,
                xref="paper", yref="paper",
                showarrow=False,
                font=dict(size=16)
            )
            fig.update_layout(
                xaxis=dict(visible=False),
                yaxis=dict(visible=False),
                template="plotly_white"
            )
            return fig

        # get the top 5, merge the rest to 'others'
        ordered_categories = pre_select.nlargest(5, ['Amount'], 'first')['Category'].tolist()  
        pre_select['Category'] = pre_select['Category'].where(pre_select['Category'].isin(ordered_categories), 'Others')      
        selection = pre_select.groupby('Category')['Amount'].sum().reset_index()

        # add 'Others' if in index (it is possible, some will have <5 categories)
        if ('Others' in selection['Category'].values):
            # append at end to ensure it is displayed last
            ordered_categories.append('Others')

        total_amount = selection['Amount'].sum()
        selection['Percentage'] = (selection['Amount'] / total_amount) * 100

        product = px.bar(selection, x = 'Amount', 
                         y = 'Category', color = 'Category', 
                         orientation='h',
                         hover_data=['Amount', 'Percentage'],
                         #height = 'auto'
                         )
        # hide legend and y-axis since Category names are specified
        product.update_layout(showlegend = False)
        product.update_layout(xaxis_title = 'Sales Amount', 
                              yaxis_title = None,
                              margin={"r":0,"t":30,"l":0,"b":0})
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
            {'display': 'block', 'color': 'white', 'font-weight': 'bold'},  # Show month label
            {'display': 'none'}    # Hide week label
        )
    else:  # Weekly
        return (
            {'display': 'none'},   # Hide monthly slider
            {'display': 'block'},  # Show weekly dropdown
            {'display': 'none'},   # Hide month label
            {'display': 'block', 'color': 'white', 'font-weight': 'bold'}  # Show week label
        )

@callback(
    Output("sales-chart-header", "children"),
    Input("time_granularity", "value")
)
def update_sales_chart_header(time_granularity):
    """
    Update the sales chart header based on the selected time granularity.

    Args:
        time_granularity (str): "Monthly" or "Weekly" from the radio button.

    Returns:
        str: Updated header text.
    """
    return "Monthly Sales" if time_granularity == "Monthly" else "Weekly Sales"