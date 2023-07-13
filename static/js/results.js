// loadSummaryData()
// New plan is:
/* 
- Load the data via the summary table
- Sort it into "grouped bar chart" dataset
- Iterate through all SVGs created in the page with a certain name
- Then make it so.
*/

var chartMargin = {top: 100, right: 20, bottom: 20, left: 30}
var config = null;
var colors = ['#f58426', '#264cf5']

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
            const metrics = [...new Set(data.map(d => d.metric.slice(0, -2)))]
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
