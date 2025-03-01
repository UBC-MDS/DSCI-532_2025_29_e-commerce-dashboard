# Milestone 2 Reflection

![Dashboard Sketch](https://raw.githubusercontent.com/UBC-MDS/DSCI-532_2025_29_e-commerce-dashboard/564ef9f8aa157555851b87a85eb7dee759ba980d/img/sketch.png)

## Changes from Dashboard Sketch
- "Collapse Menu" toggle not implemented since there's enough horizontal real estate in the dashboard right now. Will re-evaluate for future milestones if needed. 

## Known Issues ## 
- Summary statistics is fixed right now and does not update based on the filtering criteria
- Colors on the map is fixed right now and does not update based on the filtering criteria (Issue #39)
- Map only supports single State selection and does not support multi selection (Issue #39)
- Pan, zoom, reset not fully tested on all the charts
- Overall dashboard theme and chart aesethetics to be improved in Milestone 3 (Issue #33)

## Deviation from Best Practice ##
- Suitability of a pie chart for product category could be reviewed. Chart could be cluttered when there are too many categories.

## Limitations and Future Improvements ##
- Dashboard is being developed with using a subset (~13,000 records) of the full data (~130,000 records). Full dashboard performance will be tested later on with the entire dataset. 
- Small quality-of-life feature can be considered for the future 
-- Highlighting the state that's been selected by the user on the map
-- A State dropdown list next to the map if the user wants to analyze a specific state and don't know where it is on the map