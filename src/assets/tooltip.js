window.dccFunctions = window.dccFunctions || {};

// Function to get the week start date from the slider value
window.dccFunctions.getWeekStartDate = function(value) {
    // Get the week_labels from the hidden Div
    const weekLabelsElement = document.getElementById("week-labels-data");
    if (!weekLabelsElement) return value; // Fallback if data isn't found
    
    const weekLabelsStr = weekLabelsElement.textContent;
    let weekLabels;
    try {
        weekLabels = JSON.parse(weekLabelsStr.replace(/'/g, '"')); // Convert single quotes to double for valid JSON
    } catch (e) {
        return value; // Fallback
    }
    
    // Extract the start date (before the "/") for the given value
    const weekRange = weekLabels[Math.round(value)]; 
    if (!weekRange) return value; 
    
    // Get the start date from the range
    const startDate = weekRange.split('/')[0]; // e.g., "2022-03-28"
    
    // Extract just the month and day (MM-DD) from the date
    const dateParts = startDate.split('-');
    if (dateParts.length !== 3) return value; 
    
    // Return as MM-DD format
    return dateParts[1] + '-' + dateParts[2]; // Returns e.g., "03-28"
};