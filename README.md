# Gapminder D3 Scatterplot (1952 vs 2007)

This project delivers a fully implemented D3.js visualization of Gapminder-style
data. It renders a scatterplot of GDP per capita (log scale) versus life
expectancy, with circle size representing population and colors grouped by
continent.

## Project Files

- `index.html` - D3.js visualization with all required steps implemented.
- `data/gapminderDataFiveYear.tsv` - Five-year dataset for 65 countries (1952-2007).
- `IMPLEMENTATION_GUIDE.md` - Quick reference and submission checklist.

## Run Locally

D3 loads the TSV file via `fetch`, so serve the folder with a local static
server (opening the file directly can block the request).

```bash
npx serve .
```

Then open the URL printed in your terminal.

## Step-by-Step Implementation (with Code Explanations)

### Step 1: Append SVG to the `.center` div

The SVG is created dynamically inside the `.center` container, ensuring the
chart is placed where the requirements expect it.

```js
const svg = d3
  .select(".center")
  .append("svg")
  .attr("width", width)
  .attr("height", height);
```

### Step 2: Load TSV data with type conversion

The TSV is loaded with a row parser to convert numeric fields. `gdpPercap` is
mapped to the x-axis and `lifeExp` to the y-axis.

```js
const parseRow = (d) => ({
  country: d.country,
  continent: d.continent,
  year: +d.year,
  lifeExp: +d.lifeExp,
  pop: +d.pop,
  gdpPercap: +d.gdpPercap,
});

d3.tsv("data/gapminderDataFiveYear.tsv", parseRow).then((data) => {
  // ...
});
```

### Step 3: Use a logarithmic x-scale

GDP per capita spans a wide range, so the x-axis uses a log scale for clarity.

```js
const x = d3
  .scaleLog()
  .domain(d3.extent(filtered, (d) => d.gdpPercap))
  .range([0, innerWidth])
  .nice();
```

### Step 4: Filter 1952 and 2007 + apply Category10 colors

Only the start and end years are plotted. Continents use Category10 colors with
opacity set to 0.8.

```js
const filtered = data.filter((d) => d.year === 1952 || d.year === 2007);
const color = d3.scaleOrdinal(d3.schemeCategory10);
```

```js
chart
  .selectAll("circle")
  .data(filtered)
  .join("circle")
  .attr("fill", (d) => color(d.continent))
  .attr("opacity", 0.8);
```

### Step 5: Radius scaled by population (4–10px)

Population is encoded with a sqrt scale so large values remain visible.

```js
const radius = d3
  .scaleSqrt()
  .domain(d3.extent(filtered, (d) => d.pop))
  .range([4, 10]);
```

### Step 6: X-axis ticks and styled labels

The x-axis uses 11 ticks formatted with `.0s`. Both axis labels are bold,
14px, and sans-serif.

```js
chart
  .append("g")
  .attr("transform", `translate(0,${innerHeight})`)
  .call(d3.axisBottom(x).ticks(11, ".0s"));
```

```js
svg
  .append("text")
  .style("font-family", "sans-serif")
  .style("font-size", "14px")
  .style("font-weight", "700");
```

### Step 7: Title and legend styling

The chart title is underlined, bold, and 16px. The legend uses 11px sans-serif
labels with Category10 color swatches.

```js
svg
  .append("text")
  .style("font-family", "sans-serif")
  .style("font-size", "16px")
  .style("font-weight", "700")
  .style("text-decoration", "underline");
```

```js
const legend = svg
  .append("g")
  .style("font-family", "sans-serif")
  .style("font-size", "11px");
```

## Data Notes

The dataset contains 65 countries across five continents from 1952–2007 in
five-year increments. Numeric fields are already stored in a D3-friendly TSV
format for easy parsing.
