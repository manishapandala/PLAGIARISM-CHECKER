const DATA_PATH = "./data/homicide-rate-unodc.csv";

const LEFT_MARGIN = 58;
const RIGHT_MARGIN = 26;
const TOP_MARGIN = 30;
const BOTTOM_MARGIN = 42;
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

function drawMetricBadge(targetId, title, value, classes) {
  const badge = document.getElementById(targetId);
  if (!badge) return;
  badge.innerHTML = `<span class="metric-title">${title}</span><span class="metric-value ${classes}">${value}</span>`;
}

function drawArrowAnnotation(svg, x1, y1, x2, y2, classes) {
  const arrow = createSvgElement("line", {
    x1,
    y1,
    x2,
    y2,
    class: classes
  });
  arrow.setAttribute("marker-end", "url(#arrowhead)");
  svg.appendChild(arrow);
}

function createArrowMarker(svg, color) {
  const defs = createSvgElement("defs");
  const marker = createSvgElement("marker", {
    id: "arrowhead",
    markerWidth: 8,
    markerHeight: 8,
    refX: 6,
    refY: 3,
    orient: "auto"
  });
  const arrowPath = createSvgElement("path", {
    d: "M0,0 L0,6 L6,3 z",
    fill: color
  });
  marker.appendChild(arrowPath);
  defs.appendChild(marker);
  svg.appendChild(defs);
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

  createArrowMarker(svg, "#2563eb");

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

  const first = data[1];
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
    x: xForYear(1997, minYear, maxYear),
    y: yForRate(8.7, minRate, maxRate),
    class: "annotation support-annotation"
  });
  annotation.textContent = "Steady long-run decline";
  svg.appendChild(annotation);

  drawArrowAnnotation(
    svg,
    xForYear(first.year, minYear, maxYear) + 6,
    yForRate(first.rate, minRate, maxRate) + 6,
    xForYear(last.year, minYear, maxYear) - 2,
    yForRate(last.rate, minRate, maxRate) - 8,
    "support-arrow"
  );

  const declinePercent = ((first.rate - last.rate) / first.rate) * 100;
  drawMetricBadge("support-badge", "1991 to 2023 change", `${declinePercent.toFixed(0)}% lower`, "support-metric");
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
    x: xForYear(2020.5, minYear, maxYear) - 6,
    y: yForRate(6.95, minRate, maxRate),
    class: "annotation oppose-annotation"
  });
  spikeLabel.textContent = "Fast spike in just 2 years";
  svg.appendChild(spikeLabel);

  const stayHigh = createSvgElement("text", {
    x: xForYear(2022.4, minYear, maxYear),
    y: yForRate(5.9, minRate, maxRate),
    class: "annotation oppose-annotation"
  });
  stayHigh.textContent = "2023 remains above pre-spike level";
  svg.appendChild(stayHigh);

  const start = data[0];
  const peak = data.reduce((best, d) => (d.rate > best.rate ? d : best), data[0]);
  const increasePercent = ((peak.rate - start.rate) / start.rate) * 100;
  drawMetricBadge("oppose-badge", "2019 to 2021 jump", `+${increasePercent.toFixed(0)}% higher`, "oppose-metric");
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
