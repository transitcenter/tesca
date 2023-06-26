console.log("Report Loaded")
console.log(results)

var plotMargin = {top: 10, right: 30, bottom: 40, left: 10}
var plotBoxWidth = d3.select("#plot").node().getBoundingClientRect().width
var plotBoxHeight = d3.select("#plot").node().getBoundingClientRect().height
var plotChartWidth = plotBoxWidth - plotMargin.left - plotMargin.right
var plotChartHeight = plotBoxHeight - plotMargin.top - plotMargin.bottom

var projectOffset = 40
var projectBarSize = 10
var projectBarOpacity = 0.7
var projectTitleOffset = 20

var programOffset = 40
var programBarSize = 10
var programBarOpacity = 0.7
var programTitleOffset = 20

var colors = ["#d7191c", "#fdae61", "#ffffbf", "#abdda4", "#2b83ba"]

var plotBox = d3.select("#plot").append('svg').attr('width', plotBoxWidth).attr('height', plotBoxHeight)
var plotSVG = plotBox.append('g').attr("transform", "translate(" + plotMargin.left + "," + plotMargin.top + ")");

updatePlot();

function updatePlot(){
    var plotBoxWidth = d3.select("#plot").node().getBoundingClientRect().width
    var plotBoxHeight = d3.select("#plot").node().getBoundingClientRect().height
    var plotChartWidth = plotBoxWidth - plotMargin.left - plotMargin.right
    var plotChartHeight = plotBoxHeight - plotMargin.top - plotMargin.bottom

    plotBox
        .attr('width', plotBoxWidth)
        .attr('height', plotBoxHeight)

    plotSVG.selectAll("*").remove();

    var x = d3.scaleLinear()
        .domain([0, 10])
        .rangeRound([plotMargin.left, plotChartWidth]);

    // PROJECT CONTEXT VISUALIZATION
    // Title
    plotSVG.append('text')
        .attr("x", x(0))
        .attr("y", projectOffset - projectTitleOffset)
        .style("alignment-baseline", "central")
        .style("text-anchor", "start")
        .style('font-weight', 'bold')
        .text('Project Scores in Context')

    // 0 to p5 marker
    plotSVG.append('line')
        .attr("x1", x(0))
        .attr("y1", projectOffset)
        .attr("x2", x(proj_context.p5))
        .attr("y2", projectOffset)
        .attr('opacity', projectBarOpacity)
        .style('stroke', colors[0])
        .style('stroke-width', projectBarSize);

    // p5 to p25 marker
    plotSVG.append('line')
        .attr("x1", x(proj_context.p5))
        .attr("y1", projectOffset)
        .attr("x2", x(proj_context.p25))
        .attr("y2", projectOffset)
        .attr('opacity', projectBarOpacity)
        .style('stroke', colors[1])
        .style('stroke-width', projectBarSize);

    // p25 to p75 marker
    plotSVG.append('line')
        .attr("x1", x(proj_context.p25))
        .attr("y1", projectOffset)
        .attr("x2", x(proj_context.p75))
        .attr("y2", projectOffset)
        .attr('opacity', projectBarOpacity)
        .style('stroke', colors[2])
        .style('stroke-width', projectBarSize);

    // p75 to p95 marker
    plotSVG.append('line')
        .attr("x1", x(proj_context.p75))
        .attr("y1", projectOffset)
        .attr("x2", x(proj_context.p95))
        .attr("y2", projectOffset)
        .attr('opacity', projectBarOpacity)
        .style('stroke', colors[3])
        .style('stroke-width', projectBarSize);

    // p95+ marker
    plotSVG.append('line')
        .attr("x1", x(proj_context.p95))
        .attr("y1", projectOffset)
        .attr("x2", x(10))
        .attr("y2", projectOffset)
        .attr('opacity', projectBarOpacity)
        .style('stroke', colors[4])
        .style('stroke-width', projectBarSize);

    // Left zero label
    plotSVG.append('text')
        .attr("x", x(0))
        .attr("y", projectOffset)
        .attr("dx", -5)
        .style("alignment-baseline", "central")
        .style("text-anchor", "end")
        .style('font-weight', 'bold')
        .text('0')

    // Right 10 label
    plotSVG.append('text')
        .attr("x", x(10))
        .attr("y", projectOffset)
        .attr("dx", 5)
        .style("alignment-baseline", "central")
        .style("text-anchor", "start")
        .style('font-weight', 'bold')
        .text('10')

    plotSVG.append('text')
        .attr("x", x(proj_context.p5))
        .attr("y", projectOffset)
        .attr("dy", 12)
        .style("alignment-baseline", "before-edge")
        .style("text-anchor", "end")
        .style("font-size", "0.7em")
        .text('5\% of sampled projects are below ' + proj_context.p5)

    plotSVG.append('text')
        .attr("x", x(proj_context.p95))
        .attr("y", projectOffset)
        .attr("dy", 12)
        .style("alignment-baseline", "before-edge")
        .style("text-anchor", "start")
        .style("font-size", "0.7em")
        .text('5\% of sampled projects are above ' + proj_context.p95)

    // Median marker
    plotSVG.append('rect')
        .attr("x", x(proj_context.median)-8)
        .attr("y", projectOffset-8)
        .attr("height", 16)
        .attr("width", 16)
        .style("fill", "#C1C1C1")

    plotSVG.append('text')
        .attr("x", x(proj_context.median))
        .attr("y", projectOffset)
        .attr("dy", -10)
        .style("alignment-baseline", "after-edge")
        .style("text-anchor", "middle")
        .style("font-size", "0.7em")
        .text('Median: ' + proj_context.median)


    // Individual project markers
    plotSVG.append('g')
        .selectAll("dot")
        .data(results)
        .enter()
        .append("rect")
        .attr("x", d => x(d.final)-1)
        .attr("y", projectOffset-projectBarSize/2)
        .attr('width', 2)
        .attr('height', projectBarSize)
        .style('fill', "black")

        
    // // PROGRAM CONTEXT VISUALIZATION
    // // Title
    // plotSVG.append('text')
    //     .attr("x", x(0))
    //     .attr("y", programOffset - programTitleOffset)
    //     .style("alignment-baseline", "central")
    //     .style("text-anchor", "start")
    //     .style('font-weight', 'bold')
    //     .text('Program Score in Context')

    // // Zero to p5 marker
    // plotSVG.append('line')
    //     .attr("x1", x(0))
    //     .attr("y1", programOffset)
    //     .attr("y2", programOffset)
    //     .attr("x2", x(prog_context.p5))
    //     .attr('opacity', programBarOpacity)
    //     .style("stroke", colors[0])
    //     .style('stroke-width', programBarSize)
    //     .style('fill', 'none')

    // // p5 to p25 marker
    // plotSVG.append('line')
    //     .attr("x1", x(prog_context.p5))
    //     .attr("y1", programOffset)
    //     .attr("y2", programOffset)
    //     .attr("x2", x(prog_context.p25))
    //     .attr('opacity', programBarOpacity)
    //     .style("stroke", colors[1])
    //     .style('stroke-width', programBarSize)
    //     .style('fill', 'none')

    // // p25 to p75 marker
    // plotSVG.append('line')
    //     .attr("x1", x(prog_context.p25))
    //     .attr("y1", programOffset)
    //     .attr("y2", programOffset)
    //     .attr("x2", x(prog_context.p75))
    //     .attr('opacity', programBarOpacity)
    //     .style("stroke", colors[2])
    //     .style('stroke-width', programBarSize)
    //     .style('fill', 'none')

    // // p75 to p95 marker
    // plotSVG.append('line')
    //     .attr("x1", x(prog_context.p75))
    //     .attr("y1", programOffset)
    //     .attr("y2", programOffset)
    //     .attr("x2", x(prog_context.p95))
    //     .attr('opacity', programBarOpacity)
    //     .style("stroke", colors[3])
    //     .style('stroke-width', programBarSize)
    //     .style('fill', 'none')

    // // p95+ marker
    // plotSVG.append('line')
    //     .attr("x1", x(prog_context.p95))
    //     .attr("y1", programOffset)
    //     .attr("y2", programOffset)
    //     .attr("x2", x(10))
    //     .attr('opacity', programBarOpacity)
    //     .style("stroke", colors[4])
    //     .style('stroke-width', programBarSize)
    //     .style('fill', 'none')

    // // p05 label
    // plotSVG.append('text')
    //     .attr("x", x(prog_context.p5))
    //     .attr("y", programOffset)
    //     .attr('dy', 12)
    //     .style('fill', '#2D2D2D')
    //     .style("alignment-baseline", "before-edge")
    //     .style("text-anchor", "end")
    //     .style("font-size", "0.7em")
    //     .text("5\% of sampled programs are below " + prog_context.p5)

    // // p95 label
    // plotSVG.append('text')
    //     .attr("x", x(prog_context.p95))
    //     .attr("y", programOffset)
    //     .attr('dy', 12)
    //     .style('fill', '#2D2D2D')
    //     .style("alignment-baseline", "before-edge")
    //     .style("text-anchor", "start")
    //     .style("font-size", "0.7em")
    //     .text("5\% of sampled programs are above " + prog_context.p95)

    // // Left zero label
    // plotSVG.append('text')
    //     .attr("x", x(0))
    //     .attr("y", programOffset)
    //     .attr("dx", -5)
    //     .style("alignment-baseline", "central")
    //     .style("text-anchor", "end")
    //     .style('font-weight', 'bold')
    //     .text('0')

    // // Right 10 label
    // plotSVG.append('text')
    //     .attr("x", x(10))
    //     .attr("y", programOffset)
    //     .attr("dx", 5)
    //     .style("alignment-baseline", "central")
    //     .style("text-anchor", "start")
    //     .style('font-weight', 'bold')
    //     .text('10')

    // // Median label
    // plotSVG.append('text')
    //     .attr("x", x(prog_context.median))
    //     .attr("y", programOffset)
    //     .attr("dy", -20)
    //     .style("alignment-baseline", "after-edge")
    //     .style("text-anchor", "middle")
    //     .style("font-size", "0.7em")
    //     .text('Median: ' + prog_context.median)
    
    // // Median marker tick
    // plotSVG.append('line')
    //     .attr("x1", x(prog_context.median))
    //     .attr("y1", programOffset)
    //     .attr('x2', x(prog_context.median))
    //     .attr("y2", programOffset-20)
    //     .style("stroke", '#C1C1C1')
    //     .style('opacity', 0.4)
    //     .style('stroke-width', 2)

    // // Median marker
    // plotSVG.append('rect')
    //     .attr("x", x(prog_context.median)-8)
    //     .attr("y", programOffset-8)
    //     .attr("height", 16)
    //     .attr("width", 16)
    //     .style("fill", "#C1C1C1")

    // // Program score marker
    // plotSVG.append('rect')
    //     .attr("x", x(prog_context.score)-6)
    //     .attr("y", programOffset-6)
    //     .attr("height", 12)
    //     .attr("width", 12)
    //     .style("fill", "#2D2D2D")

    // plotSVG.append('text')
    //     .attr("x", x(prog_context.score))
    //     .attr("y", programOffset)
    //     .attr("dy", -8)
    //     .style("alignment-baseline", "after-edge")
    //     .style("text-anchor", "middle")
    //     .style("font-size", "0.7em")
    //     .text('This Program: ' + prog_context.score)

    

}