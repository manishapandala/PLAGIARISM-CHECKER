(() => {
  const d3 = window.d3;
  if (!d3 || typeof d3.sankey !== "function") {
    // Keep failure mode explicit if external libraries fail to load.
    throw new Error("D3 and d3-sankey must be loaded before cursoragent.js.");
  }

  const CHARACTER_GROUPS = {
    consonants: "bcdfghjklmnpqrstvwxz".split(""),
    vowels: "aeiouy".split(""),
    punctuation: ".,!?:;".split(""),
  };

  const GROUP_ORDER = ["consonants", "vowels", "punctuation"];

  const COLOR_BY_GROUP = d3
    .scaleOrdinal()
    .domain(GROUP_ORDER)
    .range(["#e9eab5", "#9fc8c1", "#b9b5d7"]);

  const GROUP_BY_CHARACTER = new Map();
  GROUP_ORDER.forEach((group) => {
    CHARACTER_GROUPS[group].forEach((char) => {
      GROUP_BY_CHARACTER.set(char, group);
    });
  });

  const textInput = document.getElementById("wordbox");
  const textHighlightLayer = document.getElementById("text_highlight_layer");
  const submitButton = document.getElementById("submit_button");
  const sankeyTitle = document.getElementById("flow_label");
  const tooltip = d3.select("#tooltip");
  const treemapSvg = d3.select("#treemap_svg");
  const sankeySvg = d3.select("#sankey_svg");
  if (
    !textInput ||
    !textHighlightLayer ||
    !submitButton ||
    !sankeyTitle ||
    treemapSvg.empty() ||
    sankeySvg.empty()
  ) {
    throw new Error("Expected chart controls and SVG containers were not found in the page.");
  }

  const appState = {
    hasSubmitted: false,
    normalizedChars: [],
    counts: createEmptyCountMap(),
    selectedChar: null,
    hoveredChar: null,
  };

  textInput.addEventListener("input", () => {
    updateTextOverlay();
  });

  textInput.addEventListener("scroll", () => {
    syncTextOverlayScroll();
  });

  submitButton.addEventListener("click", () => {
    setHoveredChar(null);
    const parsed = parseInputText(textInput.value || "");
    appState.hasSubmitted = true;
    appState.normalizedChars = parsed.normalizedChars;
    appState.counts = parsed.counts;
    appState.selectedChar = null;

    hideTooltip();
    updateTextOverlay();
    renderTreemap();
    clearSankey();
  });

  window.addEventListener("resize", () => {
    if (!appState.hasSubmitted) {
      return;
    }

    renderTreemap();
    if (appState.selectedChar) {
      renderSankey(appState.selectedChar);
    }

    syncTextOverlayScroll();
  });

  updateTextOverlay();

  function createEmptyCountMap() {
    const counts = new Map();
    GROUP_ORDER.forEach((group) => {
      CHARACTER_GROUPS[group].forEach((char) => {
        counts.set(char, 0);
      });
    });
    return counts;
  }

  function parseInputText(rawText) {
    const counts = createEmptyCountMap();
    const normalizedChars = [];
    const lower = rawText.toLowerCase();

    for (const char of lower) {
      if (!GROUP_BY_CHARACTER.has(char)) {
        continue;
      }
      counts.set(char, (counts.get(char) || 0) + 1);
      normalizedChars.push(char);
    }

    return { counts, normalizedChars };
  }

  function buildTreemapHierarchy() {
    return {
      name: "characters",
      children: GROUP_ORDER.map((group) => ({
        name: group,
        group,
        children: CHARACTER_GROUPS[group].map((char) => ({
          name: char,
          char,
          group,
          value: appState.counts.get(char) || 0,
        })),
      })),
    };
  }

  function updateSankeyTitle(char = null) {
    sankeyTitle.textContent = char
      ? `Character flow for '${char}'`
      : "Character flow for ...";
  }

  function clearSankey() {
    sankeySvg.selectAll("*").remove();
    updateSankeyTitle(null);
  }

  function drawEmptyState(svgSelection, message) {
    const { width, height } = getSvgSize(svgSelection);
    svgSelection
      .append("text")
      .attr("class", "empty-state")
      .attr("x", width / 2)
      .attr("y", height / 2)
      .text(message);
  }

  function getSvgSize(svgSelection) {
    const bounds = svgSelection.node().getBoundingClientRect();
    const width = Math.max(200, bounds.width || 200);
    const height = Math.max(200, bounds.height || 200);

    svgSelection.attr("viewBox", `0 0 ${width} ${height}`);

    return { width, height };
  }

  function renderTreemap() {
    treemapSvg.selectAll("*").remove();
    hideTooltip();

    const { width, height } = getSvgSize(treemapSvg);
    const margin = 10;
    const chartWidth = Math.max(10, width - margin * 2);
    const chartHeight = Math.max(10, height - margin * 2);

    if (appState.normalizedChars.length === 0) {
      drawEmptyState(treemapSvg, "No vowels, consonants, or punctuation found.");
      return;
    }

    const root = d3
      .hierarchy(buildTreemapHierarchy())
      .sum((d) => d.value || 0)
      .sort((a, b) => b.value - a.value);

    d3.treemap().size([chartWidth, chartHeight]).paddingInner(3).paddingOuter(4)(root);

    const leaves = root.leaves().filter((leaf) => leaf.value > 0);
    const chartGroup = treemapSvg
      .append("g")
      .attr("transform", `translate(${margin}, ${margin})`);

    chartGroup
      .selectAll("rect.char-rect")
      .data(leaves, (d) => d.data.char)
      .join("rect")
      .attr("class", "char-rect")
      .attr("x", (d) => d.x0)
      .attr("y", (d) => d.y0)
      .attr("width", (d) => Math.max(0, d.x1 - d.x0))
      .attr("height", (d) => Math.max(0, d.y1 - d.y0))
      .attr("fill", (d) => COLOR_BY_GROUP(d.data.group))
      .attr("stroke", "#000")
      .attr("stroke-width", 1)
      .style("cursor", "pointer")
      .on("mouseover", (event, d) => {
        setHoveredChar(d.data.char);
        const html = `Character: <strong>${d.data.char}</strong><br />Count: <strong>${d.data.value}</strong>`;
        showTooltip(html, event);
      })
      .on("mousemove", (event) => {
        moveTooltip(event);
      })
      .on("mouseout", () => {
        hideTooltip();
        setHoveredChar(null);
      })
      .on("click", (_, d) => {
        appState.selectedChar = d.data.char;
        updateTreemapSelection();
        renderSankey(d.data.char);
      });

    updateTreemapSelection();
  }

  function updateTreemapSelection() {
    treemapSvg
      .selectAll("rect.char-rect")
      .attr("stroke", (d) => {
        if (appState.hoveredChar && d.data.char === appState.hoveredChar) {
          return "#d97706";
        }
        if (d.data.char === appState.selectedChar) {
          return "#111827";
        }
        return "#000";
      })
      .attr("stroke-width", (d) => {
        if (appState.hoveredChar && d.data.char === appState.hoveredChar) {
          return 3;
        }
        if (d.data.char === appState.selectedChar) {
          return 2;
        }
        return 1;
      });
  }

  function updateSankeyHighlights() {
    sankeySvg
      .selectAll("rect.sankey-node-rect")
      .attr("stroke", (d) => {
        if (appState.hoveredChar && d.char === appState.hoveredChar) {
          return "#d97706";
        }
        if (appState.selectedChar && d.side === "middle") {
          return "#111827";
        }
        return "#000";
      })
      .attr("stroke-width", (d) => {
        if (appState.hoveredChar && d.char === appState.hoveredChar) {
          return 3;
        }
        if (appState.selectedChar && d.side === "middle") {
          return 2;
        }
        return 1;
      });
  }

  function buildSankeyData(selectedChar) {
    const incoming = new Map();
    const outgoing = new Map();
    const chars = appState.normalizedChars;
    const selectedCount = appState.counts.get(selectedChar) || 0;

    for (let i = 0; i < chars.length; i += 1) {
      if (chars[i] !== selectedChar) {
        continue;
      }

      if (i > 0) {
        const leftChar = chars[i - 1];
        incoming.set(leftChar, (incoming.get(leftChar) || 0) + 1);
      }

      if (i < chars.length - 1) {
        const rightChar = chars[i + 1];
        outgoing.set(rightChar, (outgoing.get(rightChar) || 0) + 1);
      }
    }

    const sortEntries = (a, b) => {
      if (b[1] !== a[1]) {
        return b[1] - a[1];
      }
      return a[0].localeCompare(b[0]);
    };

    const leftEntries = Array.from(incoming.entries()).sort(sortEntries);
    const rightEntries = Array.from(outgoing.entries()).sort(sortEntries);

    const nodes = [];
    const links = [];
    const middleNodeId = `middle:${selectedChar}`;

    leftEntries.forEach(([char, count]) => {
      const id = `left:${char}`;
      nodes.push({
        id,
        char,
        side: "left",
        group: GROUP_BY_CHARACTER.get(char),
        count,
      });
      links.push({
        source: id,
        target: middleNodeId,
        value: count,
        hidden: false,
      });
    });

    nodes.push({
      id: middleNodeId,
      char: selectedChar,
      side: "middle",
      group: GROUP_BY_CHARACTER.get(selectedChar),
      count: selectedCount,
    });

    rightEntries.forEach(([char, count]) => {
      const id = `right:${char}`;
      nodes.push({
        id,
        char,
        side: "right",
        group: GROUP_BY_CHARACTER.get(char),
        count,
      });
      links.push({
        source: middleNodeId,
        target: id,
        value: count,
        hidden: false,
      });
    });

    // Hidden balancing nodes keep the middle node proportional to total selected count.
    const incomingTotal = leftEntries.reduce((sum, entry) => sum + entry[1], 0);
    const outgoingTotal = rightEntries.reduce((sum, entry) => sum + entry[1], 0);
    const missingIncoming = Math.max(0, selectedCount - incomingTotal);
    const missingOutgoing = Math.max(0, selectedCount - outgoingTotal);

    if (missingIncoming > 0) {
      const hiddenLeftId = "hidden:left-boundary";
      nodes.push({
        id: hiddenLeftId,
        char: "",
        side: "left",
        group: "punctuation",
        count: missingIncoming,
        hidden: true,
      });
      links.push({
        source: hiddenLeftId,
        target: middleNodeId,
        value: missingIncoming,
        hidden: true,
      });
    }

    if (missingOutgoing > 0) {
      const hiddenRightId = "hidden:right-boundary";
      nodes.push({
        id: hiddenRightId,
        char: "",
        side: "right",
        group: "punctuation",
        count: missingOutgoing,
        hidden: true,
      });
      links.push({
        source: middleNodeId,
        target: hiddenRightId,
        value: missingOutgoing,
        hidden: true,
      });
    }

    return { nodes, links, selectedCount };
  }

  function renderSankey(selectedChar) {
    sankeySvg.selectAll("*").remove();
    hideTooltip();
    updateSankeyTitle(selectedChar);

    const selectedCount = appState.counts.get(selectedChar) || 0;
    if (selectedCount <= 0) {
      drawEmptyState(sankeySvg, "No flows found for selected character.");
      return;
    }

    const { width, height } = getSvgSize(sankeySvg);
    const sankeyData = buildSankeyData(selectedChar);
    const margin = { top: 10, right: 56, bottom: 10, left: 56 };

    const layout = d3
      .sankey()
      .nodeId((d) => d.id)
      .nodeWidth(Math.max(16, Math.round(width * 0.045)))
      .nodePadding(10)
      .nodeSort(null)
      .extent([
        [margin.left, margin.top],
        [Math.max(margin.left + 1, width - margin.right), Math.max(margin.top + 1, height - margin.bottom)],
      ]);

    const graph = layout({
      nodes: sankeyData.nodes.map((node) => ({ ...node })),
      links: sankeyData.links.map((link) => ({ ...link })),
    });

    const linkGroup = sankeySvg.append("g");
    linkGroup
      .selectAll("path")
      .data(graph.links)
      .join("path")
      .attr("d", d3.sankeyLinkHorizontal())
      .attr("fill", "none")
      .attr("stroke", "#bdbec1")
      .attr("stroke-opacity", (d) => (d.hidden ? 0 : 0.78))
      .attr("stroke-width", (d) => (d.hidden ? 0 : Math.max(1, d.width)))
      .attr("pointer-events", "none");

    const visibleNodes = graph.nodes.filter((node) => !node.hidden);
    const nodeGroups = sankeySvg.append("g").selectAll("g").data(visibleNodes).join("g");

    nodeGroups
      .append("rect")
      .attr("class", "sankey-node-rect")
      .attr("x", (d) => d.x0)
      .attr("y", (d) => d.y0)
      .attr("width", (d) => Math.max(0, d.x1 - d.x0))
      .attr("height", (d) => Math.max(0, d.y1 - d.y0))
      .attr("rx", 4)
      .attr("ry", 4)
      .attr("fill", (d) => COLOR_BY_GROUP(d.group))
      .attr("stroke", "#000")
      .attr("stroke-width", 1)
      .on("mouseover", (event, d) => {
        setHoveredChar(d.char);
        showTooltip(getSankeyTooltipText(d, selectedChar, sankeyData.selectedCount), event);
      })
      .on("mousemove", (event) => {
        moveTooltip(event);
      })
      .on("mouseout", () => {
        hideTooltip();
        setHoveredChar(null);
      });

    nodeGroups
      .append("text")
      .attr("x", (d) => {
        if (d.side === "left") {
          return d.x0 - 8;
        }
        if (d.side === "right") {
          return d.x1 + 8;
        }
        return (d.x0 + d.x1) / 2;
      })
      .attr("y", (d) => (d.y0 + d.y1) / 2)
      .attr("dy", "0.35em")
      .attr("text-anchor", (d) => {
        if (d.side === "left") {
          return "end";
        }
        if (d.side === "right") {
          return "start";
        }
        return "middle";
      })
      .style("font-size", `${Math.max(16, Math.min(30, width * 0.035))}px`)
      .style("fill", "#202124")
      .style("pointer-events", "none")
      .text((d) => d.char);

    updateSankeyHighlights();
  }

  function getSankeyTooltipText(node, selectedChar, selectedCount) {
    if (node.side === "left") {
      return `Character '${node.char}' flows into '${selectedChar}' <strong>${node.count}</strong> times.`;
    }
    if (node.side === "right") {
      return `Character '${selectedChar}' flows into '${node.char}' <strong>${node.count}</strong> times.`;
    }
    return `Character '${selectedChar}' appears <strong>${selectedCount}</strong> times.`;
  }

  function setHoveredChar(char) {
    const normalized = char ? char.toLowerCase() : null;
    if (appState.hoveredChar === normalized) {
      return;
    }

    appState.hoveredChar = normalized;
    updateTreemapSelection();
    updateSankeyHighlights();
    updateTextOverlay();
  }

  function updateTextOverlay() {
    const rawText = textInput.value || "";
    textHighlightLayer.innerHTML = buildTextOverlayMarkup(rawText, appState.hoveredChar);
    syncTextOverlayScroll();
  }

  function syncTextOverlayScroll() {
    textHighlightLayer.scrollTop = textInput.scrollTop;
    textHighlightLayer.scrollLeft = textInput.scrollLeft;
  }

  function buildTextOverlayMarkup(rawText, hoveredChar) {
    if (!rawText) {
      return "";
    }

    const targetChar = hoveredChar ? hoveredChar.toLowerCase() : null;
    if (!targetChar || !GROUP_BY_CHARACTER.has(targetChar)) {
      return preserveTrailingNewline(escapeHtml(rawText), rawText);
    }

    const highlightClass = `highlight-char highlight-${GROUP_BY_CHARACTER.get(targetChar)}`;
    let html = "";
    for (const char of rawText) {
      const escapedChar = escapeHtml(char);
      if (char.toLowerCase() === targetChar) {
        html += `<mark class="${highlightClass}">${escapedChar}</mark>`;
      } else {
        html += escapedChar;
      }
    }

    return preserveTrailingNewline(html, rawText);
  }

  function preserveTrailingNewline(htmlText, rawText) {
    if (rawText.endsWith("\n")) {
      return `${htmlText}\n`;
    }
    return htmlText;
  }

  function escapeHtml(text) {
    return text
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;")
      .replace(/"/g, "&quot;")
      .replace(/'/g, "&#39;");
  }

  function showTooltip(html, event) {
    tooltip.html(html).style("opacity", 1).attr("aria-hidden", "false");
    moveTooltip(event);
  }

  function moveTooltip(event) {
    tooltip.style("left", `${event.clientX}px`).style("top", `${event.clientY}px`);
  }

  function hideTooltip() {
    tooltip.style("opacity", 0).attr("aria-hidden", "true");
  }
})();
