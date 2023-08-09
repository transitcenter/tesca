
let countyData = []

loadCountyData()


function loadCountyData() {
    d3.csv("/static/data/states_counties.csv")
        .then(function (data) {
            // let states = [... new Set(data.map(d => [d.STATE, d.STATEFP]))]
            countyData = data
            let states = [...new Map(data.map(d => [d["STATE"], d])).values()].sort((a, b) => {
                let sa = a.STATE.toLowerCase(),
                    sb = b.STATE.toLowerCase();

                if (sa < sb) {
                    return -1;
                }
                if (sa > sb) {
                    return 1;
                }
                return 0;
            })
            d3.select("#states").selectAll("option")
                .data(states)
                .enter()
                .append("option")
                .text(d => d["STATE"])
                .attr("value", d => d["STATEFP"])

            stateSelectChanged()
        })
}

function stateSelectChanged() {
    let stateSelect = document.getElementById("states")
    let selectedIndex = stateSelect.selectedIndex
    let selectedStateFP = stateSelect[selectedIndex].value
    var stateCounties = countyData.filter((state) => state.STATEFP == selectedStateFP)
    stateCounties = [...new Map(stateCounties.map(d => [d["COUNTY"], d])).values()].sort((a, b) => {
        let sa = a.COUNTY.toLowerCase(),
            sb = b.COUNTY.toLowerCase();

        if (sa < sb) {
            return -1;
        }
        if (sa > sb) {
            return 1;
        }
        return 0;
    })
    // Remove the existing options
    d3.select("#counties").selectAll("option").remove()

    // Add more back in
    d3.select("#counties").selectAll("option")
        .data(stateCounties)
        .enter()
        .append("option")
        .text(d => "(" + d["COUNTYFP"] + ") " + d["COUNTY"])
        .attr("value", d => d["COUNTYFP"])
}

function addSelectedCounties() {

    let stateSelect = document.getElementById("states")
    let selectedIndex = stateSelect.selectedIndex
    let selectedStateFP = stateSelect[selectedIndex].value
    let selectedStateName = stateSelect[selectedIndex].text

    var selected = [];
    let countySelect = document.getElementById("counties")
    let selectedCountiesSelect = document.getElementById("selected-counties")
    for (var option of selectedCountiesSelect.options) {
        selected.push({value: option.value, text: option.text})
    }
    let selectedCountiesArray = [...selectedCountiesSelect.options].map(o => o.value)
    // let selectedCountiesObjectArray = [...selectedCountiesSelect.options].map(o => [o.value, o])

    for (var option of countySelect.options) {
        if (option.selected) {
            // Double-check it's not already an option
            var countyValue = selectedStateFP + option.value
            if (!selectedCountiesArray.includes(countyValue)) {
                selected.push({value: countyValue, text: "(" + countyValue + ") " + option.text.slice(5) + ", " + selectedStateName})
            }
        }
    }
    selected = selected.sort((a, b) => {
        let sa = a.value.toLowerCase(),
            sb = b.value.toLowerCase();
        if (sa < sb) {
            return -1;
        }
        if (sa > sb) {
            return 1;
        }
        return 0;
    })
    d3.select("#selected-counties").selectAll("option").remove()
    d3.select("#selected-counties").selectAll("option")
        .data(selected)
        .enter()
        .append("option")
        .text(d => d.text)
        .attr("value", d => d.value)

    checkForAnySelectedCounties()
}

function removeSelectedCounties() {
    let selectedCountiesSelect = document.getElementById("selected-counties")
    let remainingCounties = [];

    for (var option of selectedCountiesSelect.options) {
        if (!option.selected) {
            remainingCounties.push({value: option.value, text: option.text})
        }
    }
    remainingCounties = remainingCounties.sort((a, b) => {
        let sa = a.value.toLowerCase(),
            sb = b.value.toLowerCase();
        if (sa < sb) {
            return -1;
        }
        if (sa > sb) {
            return 1;
        }
        return 0;
    })

    d3.select("#selected-counties").selectAll("option").remove()
    d3.select("#selected-counties").selectAll("option")
        .data(remainingCounties)
        .enter()
        .append("option")
        .text(d => d.text)
        .attr("value", d => d.value)

    checkForAnySelectedCounties()
}

function checkForAnySelectedCounties() {
    var button = document.getElementById("fetch")
    if (document.getElementById("selected-counties").options.length > 0) {
        button.disabled = false;
    }
    else {
        button.disabled = true;
    }
}

function makeAllSelected() {
    selectedCountiesForm = document.getElementById("selected-counties-form")
    let selectedCountiesSelect = document.getElementById("selected-counties")
    for (var option of selectedCountiesSelect) {
        option.selected = true;
    }
}