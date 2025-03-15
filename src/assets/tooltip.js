window.dccFunctions = window.dccFunctions || {};

// Function to get the week start date from the slider value
window.dccFunctions.getWeekStartDate = function(value) {
    // Get the week_labels from the hidden Div
    const weekLabelsElement = document.getElementById("week-labels-data");
    if (!weekLabelsElement) return value; // Fallback
    
    const weekLabelsStr = weekLabelsElement.textContent;
    let weekLabels;
    try {
        weekLabels = JSON.parse(weekLabelsStr.replace(/'/g, '"')); 
    } catch (e) {
        return value; // Fallback
    }
    
    //get the start date 
    const weekRange = weekLabels[Math.round(value)]; 
    if (!weekRange) return value; 
    
    //start date in the range
    const startDate = weekRange.split('/')[0]; // e.g., "2022-03-28"
    
    // extract the year, month, and day from the date
    const dateParts = startDate.split('-');
    if (dateParts.length !== 3) return value; 
    
    const year = dateParts[0];  // e.g., "2022"
    const month = parseInt(dateParts[1], 10); // e.g., 3 (converted from "03")
    const day = dateParts[2];   // e.g., "28"
    
    //month abbreviations
    const monthNames = [
        "Jan", "Feb", "Mar", "Apr", "May", "Jun",
        "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"
    ];
    
    //get the month abbreviation (subtract 1 because months are 0-indexed in JS Date)
    const monthAbbr = monthNames[month - 1];
    if (!monthAbbr) return value; // Fallback if invalid
    
    //return the formatted date
    return monthAbbr + ' ' + parseInt(day, 10); // Remove leading zero from day
};