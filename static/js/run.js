// Load the log and status information on page load
window.onload = function () {
    updateLogTable();
    updateStatusMessage();
};

// Update the log and status info every few seconds.
window.setInterval(updateLogTable, 2000)
window.setInterval(updateStatusMessage, 2000)

/**
 * Update the table showing the logfile information.
 */
function updateLogTable() {
    //Fetch the logfile and JSONify it
    fetch('/info/' + analysis_id)
        .then(res => res.json())
        .then(function (data) {
            // Grab the existing table body and create a new table body to replace it
            var logTable = document.getElementById("logtable-body");
            var newTable = document.createElement("tbody");
            newTable.id = "logtable-body";

            // For each row in the data, append an appropriate table row
            data.forEach(function (item, index) {
                var tableRow = newTable.insertRow(0);

                var levelCell = tableRow.insertCell(0);
                var timeCell = tableRow.insertCell(1);
                var messageCell = tableRow.insertCell(2);

                timeCell.innerHTML = item.timestamp
                messageCell.innerHTML = item.message

                // Add a button for the error/warning/info
                button = document.createElement("button")
                var buttonClass = "button-info"
                if (item.level == "WARNING") {
                    buttonClass = "button-warning"
                } else if (item.level == "ERROR") {
                    buttonClass = "button-error"
                }
                button.setAttribute("class", "pure-button button-log " + buttonClass)
                button.innerHTML = item.level
                levelCell.appendChild(button)
            })
            logTable.parentNode.replaceChild(newTable, logTable);
        })
        .catch(err => {throw err});
}

/**
 * Update the status message.
 */
function updateStatusMessage() {
    // Fetch the status data via the API
    fetch('/status/' + analysis_id)
        .then(res => res.json())
        .then(function (data) {
            // Change the status message element
            var statusMessage = document.getElementById("status-message");
            statusMessage.innerHTML = data.message

            // If the status message is complete, show the buttons for review and run
            if (data.value == 100) {
                document.querySelectorAll(".hide-until-ready").forEach(function (item, index) {
                    item.style.visibility = "visible";
                })
            }
        })
        .catch(err => {throw err});
}