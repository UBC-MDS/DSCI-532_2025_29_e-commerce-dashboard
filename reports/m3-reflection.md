# Milestone 3 Reflection

## Dashboard Sketch ##

![](https://raw.githubusercontent.com/UBC-MDS/DSCI-532_2025_29_e-commerce-dashboard/564ef9f8aa157555851b87a85eb7dee759ba980d/img/sketch.png)

**Implemented:**

This Milestone (Milestone 3):

- Implemented update of summary statistics based on filtered data
- Added summary bar chart showing top (and selected) states sales amount
- Improvements to the geospatial plot aesthetics
- Improvement to line chart aesthetics
- Replaced "Sales by Category" pie chart with a bar chart
- Added option to filter data by weeks (in addition to monthly)
- Aggregated [data](data/amazon_sample.zip) along all usable dimensions into
- Increased [sample of data](data/amazon_sample.zip) used in the chart to 50% of original data
- Use of color channel and up/down triangle to communicate increase and change in summary metrics

Milestone 2:

- 3 summary statistic cards
- 4 types of filtering elements
- 1 geospatial plot
- 1 line chart
- 1 pie chart

**Not implemented:**

- Peer review feedback (except those already scheduled for Milestone 3)
- "Collapse Menu" toggle

## Changes from Dashboard Sketch

- "Collapse Menu" toggle not implemented since there's enough horizontal real estate in the dashboard right now. We are still evaluating this for future milestones if needed. 
- Map looks slightly different due to using a different geojson file
- Addition of 4th visualization (bar chart) in the top right main panel
- Addition of Monthly/Weekly filter toggle
- Summary metrics moved to the top of right hand side panel while search filters cover entire left hand side

## Known Issues ## 
- Color for "Others" category on "Sales by State" ends up being highest after amalgamation of non-top states (#97)
- Summary metric computation for weekly filter option not correct (#98)
- Weekly filter options and tooltips not user friendly (#99)
- Some have elements (map, line chart, tooltips) have not been updated to display Indian Rupee format yet (#100)

## Deviation from Best Practice ##


## Limitations and Future Improvements ##
- Using aggregated data helped increase the used records to ~65,000 records (~5,500 summarized rows). Full dashboard performance will be tested later on with the entire dataset.  
- Quality-of-life feature can be considered for the future 
    - Highlighting the sales of the state that's been selected by the user on the bar chart
    - A State dropdown list next to the map if the user wants to analyze a specific state and don't know where it is on the map
    - Adding multi-select for state on the map
