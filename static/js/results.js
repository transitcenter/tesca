// loadSummaryData()
// New plan is:
/* 
- Load the data via the summary table
- Sort it into "grouped bar chart" datasets
- Iterate through all SVGs created in the page with a certain name
- Then make it so.
*/

var chartNodes = d3.selectAll(".result-chart").nodes()

// Some parameters
var summaryColumns = 3
var summaryPadding = 10
var summaryData = new Array


var summaryChartMargin = {top: 50, right: 60, bottom: 40, left: 30}
var summaryBoxWidth = d3.select("#summary-chart").node().getBoundingClientRect().width
var summaryBoxHeight = d3.select("#summary-chart").node().getBoundingClientRect().height
var summaryChartWidth = summaryBoxWidth - summaryChartMargin.left - summaryChartMargin.right
var summaryChartHeight = summaryBoxHeight - summaryChartMargin.top - summaryChartMargin.bottom

var summaryInnerChartMargin = {top: 10, right: 10, bottom: 10, left: 10}

// Append the SVG
var summaryBox = d3.select("#summary-chart").append('svg').attr('width', summaryBoxWidth).attr('height', summaryBoxHeight)
var summarySVG = summaryBox.append('g').attr("transform", "translate(" + summaryChartMargin.left + "," + summaryChartMargin.top + ")");

function loadSummaryData(filter_plot) {
    d3.csv("/cache/" + analysis_id + "/summary.csv")
        .then(function (data) {
            // Filter the data by comparison
            data = data.filter(d => d.metric.slice(-3) == "1-0")
            data.forEach((d, i) => {
                d.metric = d.metric.slice(0, -4);
                var dataKeys = Object.keys(d).filter(x => x != "metric")
                var dataArray = {
                    demographic: [],
                    value: []
                }
                dataKeys.forEach((k, x) => {
                    dataArray.demographic.push(k);
                    dataArray.value.push(d[k])
                })
                var parameter = d.metric.split("_").at(-1).slice(1);
                var method = d.metric.split("_").at(-1).at(0);
                var opportunity = d.metric.slice(0, -1 * (method.length + parameter.length + 1));
                d.method = method;
                d.parameter = parseInt(parameter);
                d.opportunity = opportunity;
                summaryData.push([{
                    method: method,
                    parameter: parameter,
                    opportunity: opportunity
                }, dataArray]);
            })
            renderSummaryChart(summaryData)
        })
}

function renderSummaryChart(data) {
    summarySVG.selectAll("*").remove();
    var rows = Math.ceil(data.length / summaryColumns);

    // Compute how to divide this up
    var chartWidth = (summaryBoxWidth - summaryPadding) / summaryColumns - summaryPadding
    var chartHeight = (summaryBoxHeight - summaryPadding) / rows - summaryPadding

    var x = d3.scaleBand()
        .domain(d3.extent(data, d => d.data.demographic))
        .range(0, chartWidth)

    // TODO: Incorporate inner margins if needed
    const plots = summarySVG.selectAll(".plot")
        .data(data)
        .enter()
        .append("g")
        .attr("transform", (d, i) => {
            return "translate(" + [(i % summaryColumns) * (summaryPadding + chartWidth) + summaryPadding, Math.floor(i / rows) * (summaryPadding + chartHeight) + summaryPadding] + ")";
        })
        .append("rect")
        .attr("width", chartWidth)
        .attr("height", chartHeight)
        .attr("fill", "#ddd")

    // Add all the circles?
    plots.selectAll(null)
        .data(d => d[1])
        .enter()
        .append("circle")
        .attr("r", 4)
        .attr("cy", d => yScale(d.ratio))
        .attr("cx", d => xScale(d.run))
    // plots.selectAll("circle")
    //     .data(d => {
    //         // console.log(d)
    //         return d
    //     })
    //     .enter()
    //     .append("circle")
}

function renderGroupedBarChart(box, svg, scores, id, margin, groups, subgroups, ylabel, groupLabels, unit, note) {
    var boxWidth = d3.select(id).node().getBoundingClientRect().width
    var boxHeight = d3.select(id).node().getBoundingClientRect().height
    var chartWidth = boxWidth - margin.left - margin.right
    var chartHeight = boxHeight - margin.top - margin.bottom

    box.attr('width', boxWidth).attr('height', boxHeight);
    svg.selectAll('*').remove();

    // var toPlot = chartData.filter(d => (d['description'] == key));

    var x = d3.scaleBand()
        .domain(groups.map(d => groupLabels[d]))
        .range([margin.left, chartWidth])
        .padding(0.2);

    var y = d3.scaleLinear()
        .domain([0, d3.max(scores, d => d.value)])
        .range([chartHeight, 0])

    var xSub = d3.scaleBand()
        .domain(subgroups)
        .range([0, x.bandwidth()])
        .padding(0.05)

    var color = d3.scaleOrdinal()
        .domain(subgroups)
        .range(['#f58426', 'purple'])

    svg.selectAll('bars')
        .data(scores)
        .enter()
        .append('rect')
        .attr("x", d => x(groupLabels[d.description]) + xSub(d.subgroup))
        .attr('y', d => y(d.value))
        .attr("width", xSub.bandwidth())
        .attr("height", d => chartHeight - y(d.value))
        .attr("fill", d => color(d.subgroup))
        .attr('opacity', 0.7)

    svg.selectAll("barLabel")
        .data(scores)
        .enter()
        .append("text")
        .attr("x", d => x(groupLabels[d.description]) + xSub(d.subgroup) + xSub.bandwidth() / 2)
        .attr('y', d => y(d.value) - 6)
        .text(d => styleNumbers(d.value) + " " + unit)
        .attr('text-anchor', 'middle')
        .attr("font-size", "0.8em")

    svg.append("g")
        .attr("transform", "translate(0," + chartHeight + ")")
        .call(d3.axisBottom(x))
        .selectAll('text')
        .style("text-anchor", "middle");

    svg.append("text")
        .attr("x", chartWidth)
        .attr('y', chartHeight + margin.bottom)
        .attr("dy", "-.75em")
        .text(note)
        .attr('text-anchor', 'end')
        .attr("font-size", "0.7em")

    // Now a legend
    svg.selectAll('legendText')
        .data(subgroups)
        .enter()
        .append("text")
        .attr("x", margin.left + 20)
        .attr('y', d => 35 - margin.top + 15 * subgroups.indexOf(d))
        .text(d => subgroupLabels[d])
        .attr('text-anchor', 'start')
        .attr('dominant-baseline', 'middle')
        .attr("font-size", "0.8em")

    svg.selectAll('legendBox')
        .data(subgroups)
        .enter()
        .append('rect')
        .attr('x', margin.left)
        .attr('y', d => 30 - margin.top + 15 * (subgroups.indexOf(d)))
        .attr('width', 10)
        .attr('height', 10)
        .attr('fill', d => color(d))
        .attr('opacity', 0.7)

    svg.append('text')
        .attr("x", margin.left)
        .attr('y', 20 - margin.top)
        .text(ylabel)
        .attr('text-anchor', 'start')
        .attr('font-weight', 'bold')
}