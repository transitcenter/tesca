let chartMargin = { top: 100, right: 20, bottom: 20, left: 30 }
let config = null;
let colors = ['#f58426', '#264cf5']

// Map configurations
const zoom = 12
const startLat = "43.715877"
const startLon = "-79.3243027"
let travelTimeDeltaColors = ["#762a83", "#af8dc3", "#e7d4e8", "#f7f7f7", "#d9f0d3", "#7fbf7b", "#1b7837"]

// Things to be updated later
let metrics = null;
let compareData = {};

// Initialize the map
let map = L.map('results-map',
    { preferCanvas: true }
).setView([startLat, startLon], zoom);

// Load the basemap layer - currently using CartoDB Greyscale.
let cartoLight = L.tileLayer("https://cartodb-basemaps-{s}.global.ssl.fastly.net/light_nolabels/{z}/{x}/{y}.png", {
    attribution: '&copy; <a href="http://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors, &copy; <a href="https://cartodb.com/attributions">CartoDB</a>'
}).addTo(map);

// Create the layer group of place labels, which sits highest
map.createPane('labels');
map.getPane('labels').style.zIndex = 650;
map.getPane('labels').style.pointerEvents = 'none';

// Grab the labels map and add it to the map.
let cartoLabels = L.tileLayer("https://cartodb-basemaps-{s}.global.ssl.fastly.net/light_only_labels/{z}/{x}/{y}.png", {
    attribution: '&copy; <a href="http://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors, &copy; <a href="https://cartodb.com/attributions">CartoDB</a>',
    pane: 'labels'
}).addTo(map);

// Add a scale bar for scale
let scaleBar = L.control.scale().addTo(map)

// Fetch and render centroids
let bgLayer = new L.GeoJSON.AJAX("/cache/" + analysis_id + "/analysis_polygons.geojson", {
    style: blockGroupStyleDefault
}).addTo(map)

// Recenter the map on the appropriate layer.
bgLayer.on('data:loaded', function () {
    map.fitBounds(bgLayer.getBounds());
}.bind(this));

loadConfigData()


/**
 * Load the configuration data into memory and call the appropriate charts
 */
function loadConfigData() {
    d3.json("/config/" + analysis_id).then(function (data) {
        config = data;
        loadSummaryData()
    })
}

// TODO:
// 1. Load the baseline map data as an initialization
// 2. Create a separate function for updating the map style 

/**
 * Load the summary data and plot the summary charts.
 * 
 * This method fetches the CSV file containing the summary data for the results, compiles it into
 * a useful format for D3, and then iteratively goes through all of the summary div elements in the page
 * and creates a chart for each of them.
 */
function loadSummaryData() {
    d3.csv("/cache/" + analysis_id + "/summary.csv")
        //d3.csv("https://raw.githubusercontent.com/holtzy/D3-graph-gallery/master/DATA/data_stacked.csv")
        .then(function (data) {
            const demographics = data.columns.slice(1)
            const scenarios = []
            config.scenarios.forEach(d => {
                scenarios.push(d.name)
            })
            const plotData = []
            data = data.filter(d => !(d.metric.slice(-3) == "1-0"))
            data.forEach((d, i) => {
                let scenario = scenarios[parseInt(d.metric.at(-1))]
                let metric = d.metric.slice(0, -2)
                demographics.forEach((demo, index) => {
                    let demographic = demo
                    let value = d[demo]
                    plotData.push({
                        scenario: scenario,
                        metric: metric,
                        demographic: demographic,
                        value: value
                    })
                })

            })
            metrics = [...new Set(data.map(d => d.metric.slice(0, -2)))]

            loadCompareData("hospitals_t1")
            metrics.forEach((metric, index) => {
                // Filter the data appropriately
                const toPlot = plotData.filter(d => d.metric == metric)
                const opportunityKey = metric.split("_").slice(0, -1).join("_")
                const method = metric.split("_").at(-1).at(0)
                const parameter = metric.split("_").at(-1).slice(1)
                const unit = config["opportunities"][opportunityKey]["unit"]
                const opportunity = config["opportunities"][opportunityKey]["name"]
                const title = "Access to " + opportunity
                let subtitle = null;
                if (method == "c") {
                    subtitle = "Average total " + unit + " reachable in " + parameter + " minutes on transit"
                }
                else {
                    subtitle = "Average minutes of travel time to reach the nearest " + parameter + " " + opportunity.toLowerCase()
                }
                renderGroupedBarChart(toPlot, String(metric), demographics, scenarios, title, subtitle)
            })
        })
}

function loadCompareData(initialMetric) {
    d3.csv("/cache/" + analysis_id + "/compared.csv")
        .then(function (data) {
            data.forEach(d => {
                compareData[d.bg_id] = d
            })
            console.log(compareData)
            updateMap(initialMetric)
        })
}


/**
 * Update the map to show changes in values between scenarios
 * @param {String} metric The metric to filter and color the map on.
 */
function updateMap(metric) {
    bgLayer.setStyle(function (feature) {
        delta = compareData[feature.properties.bg_id][metric + "_1-0"]
        const thisColor = getTravelTimeDeltaColor(delta, travelTimeDeltaColors)
        return {
            fillColor: thisColor,
            color: thisColor
        }
    })
    bgLayer.eachLayer(function (layer) {
        delta = compareData[layer.feature.properties.bg_id][metric + "_1-0"]
        layer.bindPopup("<b>Delta</b>: " + styleNumbers(delta))
    })
    // travelTimeDeltaColors
}

/**
 * 
 * @param {Object} data A dictionary containing the relevant bar chart data
 * @param {String} id The element ID to create the plot in
 * @param {Array} groups A list of the groups (demographics) to plot
 * @param {Array} subgroups A list of the subgroups to make the "grouped" in grouped bar chart
 * @param {String} title The title to append to the chart
 * @param {String} subtitle The subtitle to append to the chart
 */
function renderGroupedBarChart(data, id, groups, subgroups, title, subtitle) {
    // Grab the appropriate SVG and get width and heigh metrics
    const chartDiv = d3.select("#" + id)
    const boxWidth = chartDiv.node().getBoundingClientRect().width
    const boxHeight = chartDiv.node().getBoundingClientRect().height
    const chartWidth = boxWidth - chartMargin.left - chartMargin.right
    const chartHeight = boxHeight - chartMargin.top - chartMargin.bottom

    // Clear everything out
    chartDiv.selectAll('*').remove();

    // Add an SVG back in
    const svg = chartDiv.append("svg").attr("class", "chart-svg")
    svg.attr('width', boxWidth).attr('height', boxHeight);

    // Dictionarify the labels to make it easier to plot
    const demoLabels = {}
    for (var key in demoStyle) {
        demoLabels[key] = demoStyle[key]['label']
    }

    // Set up the major X xcale (demographic categories)
    var x = d3.scaleBand()
        .domain(groups.map(d => demoLabels[d]))
        .range([0, chartWidth])
        .padding(0.15);

    // Set up the Y axis scale
    var y = d3.scaleLinear()
        .domain([0, d3.max(data, d => d.value)])
        .range([chartHeight, chartMargin.top])

    // Set up the inner scale for the groups (gets added to the outer scale)
    var xSub = d3.scaleBand()
        .domain(subgroups)
        .range([0, x.bandwidth()])
        .padding(0.1)

    // Set up the color scale for the subgroups.
    var color = d3.scaleOrdinal()
        .domain(subgroups)
        .range(colors)

    // Create the bars themselves
    svg.selectAll('bars')
        .data(data)
        .enter()
        .append('rect')
        .attr("x", d => x(demoLabels[d.demographic]) + xSub(d.scenario))
        .attr('y', d => y(d.value))
        .attr("width", xSub.bandwidth())
        .attr("height", d => chartMargin.top + chartHeight - y(d.value))
        .attr("fill", d => color(d.scenario))
        .attr('rx', 5)
        .attr('opacity', 0.6)

    // Add a label to the top of the bars
    svg.selectAll("barLabel")
        .data(data)
        .enter()
        .append("text")
        .attr("x", d => x(demoLabels[d.demographic]) + xSub(d.scenario) + xSub.bandwidth() / 2)
        .attr('y', d => y(d.value) - 6)
        .text(d => styleNumbers(d.value))
        .attr('text-anchor', 'middle')
        .attr("font-size", "0.6em")

    // Add the bottom axis for the charts
    svg.append("g")
        .attr("transform", "translate(0," + (chartMargin.top + chartHeight) + ")")
        .call(d3.axisBottom(x).tickSize(0))
        .call(g => g.select(".domain").remove())  // This removes the domain axis
        .selectAll('text')
        .style("text-anchor", "middle")
        .attr("dy", "1em")


    // Adding a title
    svg.append("text")
        .attr("x", chartMargin.left)
        .attr("y", 20)
        .text(title)
        .style("font-weight", "bold")
        .attr("font-size", "18px")

    // Adding a subtitle
    svg.append("text")
        .attr("x", chartMargin.left)
        .attr("y", 35)
        .text(subtitle)
        .attr("font-size", "14px")

    // Now a legend
    svg.selectAll('legendText')
        .data(subgroups)
        .enter()
        .append("text")
        .attr("x", chartMargin.left + 15)
        .attr('y', d => 45 + 15 * subgroups.indexOf(d))
        .text(d => d)
        .attr('text-anchor', 'start')
        .attr('dominant-baseline', 'hanging')
        .attr("font-size", "12px")

    // And boxes to represent the legend
    svg.selectAll('legendBox')
        .data(subgroups)
        .enter()
        .append('rect')
        .attr('x', chartMargin.left)
        .attr('y', d => 45 + 15 * (subgroups.indexOf(d)))
        .attr('width', 10)
        .attr('height', 10)
        .attr('fill', d => color(d))
        .attr('opacity', 0.6)
        .attr('rx', 2)
}

function blockGroupStyleDefault(feature) {
    return {
        fillColor: 'none',
        weight: 1,
        opacity: 0.1,
        color: 'none',
        fillOpacity: 0.7
    };
}

/**
 * This function styles numbers based on their magnitutde. Numbers greater than 1,000
 * are styled using a 'k' to represent thousands, with an aim of having at least two
 * significant digits for all numbers.
 * @param {Number} val The value to style
 * @returns A styled value string for display.
 */
function styleNumbers(val) {
    val = parseFloat(val)
    if (Math.abs(val) >= 10000) {
        return (val / 1000).toFixed(0).toString().replace(/\B(?=(\d{3})+(?!\d))/g, ",") + "k";
    }
    else if (Math.abs(val) >= 1000) {
        return (val / 1000).toFixed(2).toString().replace(/\B(?=(\d{3})+(?!\d))/g, ",") + "k";
    }
    else if (Math.abs(val) > 10) {
        return val.toFixed(0)
    }
    else if (val == 0.0) {
        return val.toFixed(0)
    }
    else {
        return val.toFixed(0)
    }
}

var demoStyle = {
    'B03002_001E': {
        'label': 'Everyone',
        'sentence': 'everyone',
        'color': "#7F7F7F"
    },
    'B03002_006E': {
        'label': "Asian",
        'sentence': 'Asian people, Native Hawaiians, and Pacific Islanders',
        'color': "#1F77B4"
    },
    'B03002_004E': {
        'label': "Black",
        'sentence': 'Black people',
        'color': "#2CA02C"
    },
    'B03002_012E': {
        'label': "Hispanic",
        'sentence': "Hispanic or Latino people",
        'color': "#D62728"
    },
    'B03002_003E': {
        'label': "White",
        'sentence': 'white people',
        'color': "#9467BD"
    },
    'C17002_003E': {
        'label': "In Poverty",
        'sentence': 'people in poverty',
        'color': '#8C564B'
    }
}


/**
 * Colour value based on pre-defiend travel time range.
 * @param {Number} data Data to quintile.
 * @param {Array} colors Array of 5 colors to use.
 */
function getTravelTimeDeltaColor(d, colors) {
    if (isNaN(d)) {
        return nan_color;
    }
    else {
        return d >= 4 ? colors[0] :
            d >= 3 ? colors[1] :
                d >= 1 ? colors[2] :
                    d >= -1 ? colors[3] :
                        d >= -3 ? colors[4] :
                            d > -5 ? colors[5] :
                                colors[6];
    }
}
