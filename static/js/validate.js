// Load the log table
window.onload = function () {
    updateLogTable();
    updateStatusMessage();
};

// Update the log table
window.setInterval(updateLogTable, 4000)
window.setInterval(updateStatusMessage, 4000)

function updateLogTable() {
    fetch('/info/' + analysis_id)
        .then(res => res.json())
        .then(function (data) {
            var logTable = document.getElementById("logtable-body");
            var newTable = document.createElement("tbody");
            newTable.id = "logtable-body";

            data.forEach(function (item, index) {
                var tableRow = newTable.insertRow(0);

                var levelCell = tableRow.insertCell(0);
                var timeCell = tableRow.insertCell(1);
                var messageCell = tableRow.insertCell(2);

                timeCell.innerHTML = item.timestamp
                messageCell.innerHTML = item.message
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

function updateStatusMessage() {
    fetch('/status/' + analysis_id)
        .then(res => res.json())
        .then(function (data) {
            var statusMessage = document.getElementById("status-message");
            statusMessage.innerHTML = data.message
            if (data.value == 100) {
                document.querySelectorAll(".hide-until-ready").forEach(function (item, index) {
                    item.style.visibility = "visible";
                })
            }
        })
        .catch(err => {throw err});
}