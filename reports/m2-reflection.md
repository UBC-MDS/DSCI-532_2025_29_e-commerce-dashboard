# Milestone 2 Reflection

## Dashboard Sketch ##

![](https://raw.githubusercontent.com/UBC-MDS/DSCI-532_2025_29_e-commerce-dashboard/564ef9f8aa157555851b87a85eb7dee759ba980d/img/sketch.png)

**Implemented:**

- 3 summary statistic cards
- 4 types of filtering elements
- 1 geospatial plot
- 1 line chart
- 1 pie chart

**Not implemented:**

- Bar chart has been changed to pie chart
- "Collapse Menu" toggle

## Changes from Dashboard Sketch
- "Collapse Menu" toggle not implemented since there's enough horizontal real estate in the dashboard right now. Will re-evaluate for future milestones if needed. 
- Map looks slightly different due to using a different geojson file
- Bar chart changed to pie chart to enable users to analyze proportions of the sales by product category

## Known Issues ## 
- Colors on the map is fixed right now and does not update based on the filtering criteria (Issue #39)
- Map only supports single State selection and does not support multi selection (Issue #39)
- Pan, zoom, reset not fully tested on all the charts
- Overall dashboard theme and chart aesethetics to be improved in Milestone 3 (Issue #33)

## Deviation from Best Practice ##
- Pie chart could be cluttered when there are too many categories. If categories are close in size, the user has to use the tooltip to view exact amount.

## Limitations and Future Improvements ##
- Summary statistics is fixed right now by design. Currently they are considered to be "current status" and not part of the analysis. However there are discussions within the group on whether these should be part of the filtering/analysis. 
- Dashboard is being developed with using a subset (~13,000 records) of the full data (~130,000 records). Full dashboard performance will be tested later on with the entire dataset. 
- Suitability of a pie chart for product category could be re-evaulated. 
- Quality-of-life feature can be considered for the future 
    - Highlighting the state that's been selected by the user on the map
    - A State dropdown list next to the map if the user wants to analyze a specific state and don't know where it is on the map