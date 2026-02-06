# Implementation Guide

Quick reference for the Gapminder D3 visualization plus a submission checklist.

## Quick Reference

- **Entry point:** `index.html`
- **Data file:** `data/gapminderDataFiveYear.tsv`
- **Chart size:** 960 x 560 (with margins)
- **Years shown:** 1952 and 2007
- **Color palette:** `d3.schemeCategory10`
- **Radius scale:** 4–10px based on population
- **X-axis:** log scale, 11 ticks, `.0s` formatting
- **Title:** 16px bold, underlined, sans-serif
- **Legend:** 11px sans-serif

## Submission Checklist

- [x] SVG appended to `.center` div.
- [x] TSV loaded with numeric type conversion.
- [x] `gdpPercap` mapped to x-axis and `lifeExp` to y-axis.
- [x] Logarithmic scale on x-axis.
- [x] Data filtered to 1952 and 2007.
- [x] Category10 colors applied with 0.8 opacity.
- [x] Circle radius scaled by population (4–10px).
- [x] X-axis uses 11 ticks and `.0s` format.
- [x] Axis labels styled sans-serif, 14px, bold.
- [x] Title styled sans-serif, 16px, bold, underlined.
- [x] Legend included with sans-serif 11px labels.
