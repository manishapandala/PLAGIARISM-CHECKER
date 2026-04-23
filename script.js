const DATA_PATH = "./data/homicide-rate-unodc.csv";

const LEFT_MARGIN = 56;
const RIGHT_MARGIN = 20;
const TOP_MARGIN = 28;
const BOTTOM_MARGIN = 40;
const INNER_WIDTH = 560 - LEFT_MARGIN - RIGHT_MARGIN;
const INNER_HEIGHT = 360 - TOP_MARGIN - BOTTOM_MARGIN;

function parseCsv(text) {
  const lines = text.trim().split("\n");
  const rows = [];

  for (let i = 1; i < lines.length; i += 1) {
    const row = lines[i];
    const cells = row.split(",");
    if (cells.length < 4) {
      continue;
    }
    rows.push({
      entity: cells[0],
      code: cells[1],
      year: Number(cells[2]),
      rate: Number(cells[3])
    });
  }

  return rows;
}

function createSvgElement(tagName, attributes = {}) {
  const element = document.createElementNS("http://www.w3.org/2000/svg", tagName);
  Object.entries(attributes).forEach(([key, value]) => {
    element.setAttribute(key, String(value));
  });
  return element;
}

function scaleLinear(value, inputMin, inputMax, outputMin, outputMax) {
  if (inputMax === inputMin) {
    return outputMin;
  }
  const t = (value - inputMin) / (inputMax - inputMin);
  return outputMin + t * (outputMax - outputMin);
}

function xForYear(year, minYear, maxYear) {
  return scaleLinear(year, minYear, maxYear, LEFT_MARGIN, LEFT_MARGIN + INNER_WIDTH);
}

function yForRate(rate, minRate, maxRate) {
  return scaleLinear(rate, minRate, maxRate, TOP_MARGIN + INNER_HEIGHT, TOP_MARGIN);
}

function buildPath(data, minYear, maxYear, minRate, maxRate) {
  return data
    .map((d, index) => {
      const x = xForYear(d.year, minYear, maxYear);
      const y = yForRate(d.rate, minRate, maxRate);
      return `${index === 0 ? "M" : "L"} ${x.toFixed(2)} ${y.toFixed(2)}`;
    })
    .join(" ");
}

function drawAxes(svg, yearTicks, rateTicks, minYear, maxYear, minRate, maxRate, classes) {
  const axisLayer = createSvgElement("g", { class: "axes" });

  const xAxis = createSvgElement("line", {
    x1: LEFT_MARGIN,
    y1: TOP_MARGIN + INNER_HEIGHT,
    x2: LEFT_MARGIN + INNER_WIDTH,
    y2: TOP_MARGIN + INNER_HEIGHT,
    class: classes.axis
  });

  const yAxis = createSvgElement("line", {
    x1: LEFT_MARGIN,
    y1: TOP_MARGIN,
    x2: LEFT_MARGIN,
    y2: TOP_MARGIN + INNER_HEIGHT,
    class: classes.axis
  });

  axisLayer.appendChild(xAxis);
  axisLayer.appendChild(yAxis);

  rateTicks.forEach((tickValue) => {
    const y = yForRate(tickValue, minRate, maxRate);
    const grid = createSvgElement("line", {
      x1: LEFT_MARGIN,
      y1: y,
      x2: LEFT_MARGIN + INNER_WIDTH,
      y2: y,
      class: classes.grid
    });
    axisLayer.appendChild(grid);

    const label = createSvgElement("text", {
      x: LEFT_MARGIN - 8,
      y: y + 4,
      "text-anchor": "end",
      class: classes.tick
    });
    label.textContent = tickValue.toFixed(1);
    axisLayer.appendChild(label);
  });

  yearTicks.forEach((tickValue) => {
    const x = xForYear(tickValue, minYear, maxYear);
    const tick = createSvgElement("line", {
      x1: x,
      y1: TOP_MARGIN + INNER_HEIGHT,
      x2: x,
      y2: TOP_MARGIN + INNER_HEIGHT + 4,
      class: classes.axis
    });
    axisLayer.appendChild(tick);

    const label = createSvgElement("text", {
      x,
      y: TOP_MARGIN + INNER_HEIGHT + 18,
      "text-anchor": "middle",
      class: classes.tick
    });
    label.textContent = String(tickValue);
    axisLayer.appendChild(label);
  });

  const yTitle = createSvgElement("text", {
    x: 16,
    y: TOP_MARGIN + INNER_HEIGHT / 2,
    transform: `rotate(-90 16 ${TOP_MARGIN + INNER_HEIGHT / 2})`,
    class: classes.label
  });
  yTitle.textContent = "Homicides per 100,000";
  axisLayer.appendChild(yTitle);

  const xTitle = createSvgElement("text", {
    x: LEFT_MARGIN + INNER_WIDTH / 2,
    y: 350,
    "text-anchor": "middle",
    class: classes.label
  });
  xTitle.textContent = "Year";
  axisLayer.appendChild(xTitle);

  svg.appendChild(axisLayer);
}

function drawSupportChart(allUsData) {
  const svg = document.getElementById("support-chart");
  if (!svg) return;
  svg.innerHTML = "";

  const data = allUsData.filter((d) => d.year >= 1990 && d.year <= 2023);
  const minYear = 1990;
  const maxYear = 2023;
  const minRate = 0;
  const maxRate = 10;

  drawAxes(
    svg,
    [1990, 2000, 2010, 2020, 2023],
    [0, 2, 4, 6, 8, 10],
    minYear,
    maxYear,
    minRate,
    maxRate,
    {
      axis: "axis support-axis",
      grid: "grid support-grid",
      tick: "tick support-tick",
      label: "axis-label support-label"
    }
  );

  const path = createSvgElement("path", {
    d: buildPath(data, minYear, maxYear, minRate, maxRate),
    class: "trend-line support-line"
  });
  svg.appendChild(path);

  const first = data[0];
  const last = data[data.length - 1];
  const firstCircle = createSvgElement("circle", {
    cx: xForYear(first.year, minYear, maxYear),
    cy: yForRate(first.rate, minRate, maxRate),
    r: 4,
    class: "point support-point"
  });
  const lastCircle = createSvgElement("circle", {
    cx: xForYear(last.year, minYear, maxYear),
    cy: yForRate(last.rate, minRate, maxRate),
    r: 4,
    class: "point support-point"
  });
  svg.appendChild(firstCircle);
  svg.appendChild(lastCircle);

  const annotation = createSvgElement("text", {
    x: xForYear(2001, minYear, maxYear),
    y: yForRate(9.2, minRate, maxRate),
    class: "annotation support-annotation"
  });
  annotation.textContent = "Down ~40% from 1991 peak to 2023";
  svg.appendChild(annotation);
}

function drawOpposeChart(allUsData) {
  const svg = document.getElementById("oppose-chart");
  if (!svg) return;
  svg.innerHTML = "";

  const data = allUsData.filter((d) => d.year >= 2019 && d.year <= 2023);
  const minYear = 2019;
  const maxYear = 2023;
  const minRate = 4.5;
  const maxRate = 7.1;

  drawAxes(
    svg,
    [2019, 2020, 2021, 2022, 2023],
    [4.5, 5.0, 5.5, 6.0, 6.5, 7.0],
    minYear,
    maxYear,
    minRate,
    maxRate,
    {
      axis: "axis oppose-axis",
      grid: "grid oppose-grid",
      tick: "tick oppose-tick",
      label: "axis-label oppose-label"
    }
  );

  const areaPathData =
    `${buildPath(data, minYear, maxYear, minRate, maxRate)} ` +
    `L ${xForYear(maxYear, minYear, maxYear)} ${yForRate(minRate, minRate, maxRate)} ` +
    `L ${xForYear(minYear, minYear, maxYear)} ${yForRate(minRate, minRate, maxRate)} Z`;

  const area = createSvgElement("path", {
    d: areaPathData,
    class: "trend-area oppose-area"
  });
  svg.appendChild(area);

  const path = createSvgElement("path", {
    d: buildPath(data, minYear, maxYear, minRate, maxRate),
    class: "trend-line oppose-line"
  });
  svg.appendChild(path);

  data.forEach((d) => {
    const point = createSvgElement("circle", {
      cx: xForYear(d.year, minYear, maxYear),
      cy: yForRate(d.rate, minRate, maxRate),
      r: 4,
      class: "point oppose-point"
    });
    svg.appendChild(point);
  });

  const spikeLabel = createSvgElement("text", {
    x: xForYear(2021, minYear, maxYear) - 20,
    y: yForRate(6.95, minRate, maxRate),
    class: "annotation oppose-annotation"
  });
  spikeLabel.textContent = "Sharp 2020-2021 surge";
  svg.appendChild(spikeLabel);

  const stayHigh = createSvgElement("text", {
    x: xForYear(2022.4, minYear, maxYear),
    y: yForRate(5.9, minRate, maxRate),
    class: "annotation oppose-annotation"
  });
  stayHigh.textContent = "2023 still above 2019";
  svg.appendChild(stayHigh);
}

function init() {
  fetch(DATA_PATH)
    .then((response) => response.text())
    .then((text) => {
      const rows = parseCsv(text);
      const usRows = rows
        .filter((row) => row.code === "USA" && Number.isFinite(row.year) && Number.isFinite(row.rate))
        .sort((a, b) => a.year - b.year);

      drawSupportChart(usRows);
      drawOpposeChart(usRows);
    })
    .catch(() => {
      const charts = document.querySelectorAll(".chart-svg");
      charts.forEach((chart) => {
        chart.innerHTML = "";
        const message = createSvgElement("text", {
          x: 280,
          y: 180,
          "text-anchor": "middle",
          class: "annotation"
        });
        message.textContent = "Failed to load data file.";
        chart.appendChild(message);
      });
    });
}

init();
