// Set the dimensions of the canvas
const margin = { top: 50, right: 140, bottom: 70, left: 70 };
const width = 800 - margin.left - margin.right;
const height = 470 - margin.top - margin.bottom;

// set the ranges
const xScale = d3.scaleLog().range([0, width]);
const yScale = d3.scaleLinear().range([height, 0]);
const radiusScale = d3.scaleLinear().range([4, 10]);

// append the svg object to the center div
const svg = d3
  .select(".center")
  .append("svg")
  .attr("width", width + margin.left + margin.right)
  .attr("height", height + margin.top + margin.bottom);

const chart = svg
  .append("g")
  .attr("transform", `translate(${margin.left},${margin.top})`);

const colorScale = d3.scaleOrdinal(d3.schemeCategory10).domain([1952, 2007]);

// Get the data
d3.tsv("data/gapminderDataFiveYear.tsv", (d) => ({
  country: d.country,
  continent: d.continent,
  year: +d.year,
  lifeExp: +d.lifeExp,
  pop: +d.pop,
  gdpPercap: +d.gdpPercap,
})).then((data) => {
  const filtered = data.filter((d) => d.year === 1952 || d.year === 2007);

  xScale.domain(d3.extent(filtered, (d) => d.gdpPercap)).nice();
  yScale.domain(d3.extent(filtered, (d) => d.lifeExp)).nice();
  radiusScale.domain(d3.extent(filtered, (d) => d.pop));

  // Add the scatterplot
  chart
    .selectAll("circle")
    .data(filtered)
    .join("circle")
    .attr("r", (d) => radiusScale(d.pop))
    .attr("cx", (d) => xScale(d.gdpPercap))
    .attr("cy", (d) => yScale(d.lifeExp))
    .attr("fill", (d) => colorScale(d.year))
    .attr("opacity", 0.8);

  // Add the axes
  const yAxis = d3.axisLeft(yScale);
  chart.append("g").call(yAxis);

  const xAxis = d3.axisBottom(xScale).ticks(11, ".0s");
  chart
    .append("g")
    .attr("transform", `translate(0,${height})`)
    .call(xAxis);

  // Axis labels
  svg
    .append("text")
    .attr("x", margin.left + width / 2)
    .attr("y", margin.top + height + 45)
    .attr("text-anchor", "middle")
    .style("font-family", "sans-serif")
    .style("font-size", "14px")
    .style("font-weight", "700")
    .text("GDP per Capita");

  svg
    .append("text")
    .attr(
      "transform",
      `translate(${margin.left - 45}, ${margin.top + height / 2}) rotate(-90)`
    )
    .attr("text-anchor", "middle")
    .style("font-family", "sans-serif")
    .style("font-size", "14px")
    .style("font-weight", "700")
    .text("Life Expectancy");

  // Title
  svg
    .append("text")
    .attr("x", margin.left + width / 2)
    .attr("y", 24)
    .attr("text-anchor", "middle")
    .style("font-family", "sans-serif")
    .style("font-size", "16px")
    .style("font-weight", "700")
    .style("text-decoration", "underline")
    .text("GDP vs Life Expectancy (1952, 2007)");

  // Legend
  const legendData = [1952, 2007];
  const legend = svg
    .append("g")
    .attr(
      "transform",
      `translate(${margin.left + width + 20}, ${margin.top})`
    )
    .style("font-family", "sans-serif")
    .style("font-size", "11px");

  const legendItem = legend
    .selectAll("g")
    .data(legendData)
    .join("g")
    .attr("transform", (d, i) => `translate(0, ${i * 18})`);

  legendItem
    .append("rect")
    .attr("width", 12)
    .attr("height", 12)
    .attr("fill", (d) => colorScale(d));

  legendItem
    .append("text")
    .attr("x", 18)
    .attr("y", 10)
    .text((d) => d);
});
