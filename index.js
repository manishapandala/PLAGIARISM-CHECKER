// Set the dimensions of the canvas

const margin = {top: 10, right: 20, bottom: 50, left: 50};
const width = 800 - margin.left - margin.right;
const height = 470 - margin.top - margin.bottom;

// parse the date / time
const parseTime = d3.timeParse("%d-%b-%y");

// set the ranges
const xScale = d3.scaleTime()
                 .range([0, width]);
const yScale = d3.scaleLinear()
                  .range([height, 0]);

// define the line
const valueline = d3.line()
                    .x(function(d) { return xScale(d.date); })
                    .y(function(d) { return yScale(d.close); });

// append the svg object to the body of the page
// append a g (group) element to 'svg' and
// move the g element to the top and left margin
var svg = d3.select("#container").append("svg")
                           .attr("width", width + margin.left + margin.right)
                           .attr("height", height + margin.top + margin.bottom)
                           .append("g")
                           .attr("transform", `translate(${margin.left},${margin.top})`);

// Get the data
d3.csv("data/dates.csv").then(data => {

    // format the data such that strings are converted to their appropriate types
    data.forEach(function(d) {
        d.date = parseTime(d.date);
        d.close = +d.close;
    });

    // Set scale domains based on the loaded data
    xScale.domain(d3.extent(data, function(d) { return d.date; }));
    yScale.domain([0, d3.max(data, function(d) { return d.close; })]);

    // Add the valueline
    svg.append("path")
        .data([data])
        .attr("class", "line")
        .attr("d", valueline);
    
    // Add the scatterplot
    svg.selectAll("dot")
        .data(data)
        .enter().append("circle")
        .attr("r", 5)
        .attr("cx", function(d) { return xScale(d.date); })
        .attr("cy", function(d) { return yScale(d.close); });
    
    // Add the axes
    const yAxis = d3.axisLeft(yScale);
    svg.append("g")
        .call(yAxis);
    const xAxis = d3.axisBottom(xScale);
    svg.append("g")
        .attr("transform", "translate(0," + height + ")")
        .call(xAxis);

});
