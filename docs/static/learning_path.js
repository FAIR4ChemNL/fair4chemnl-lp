/*
 * Reusable d3.js renderer for Bloom's-taxonomy based learning path slides.
 *
 *   LearningPath.render("#chart", "data/inchi.json", { background: "background/learning_path.png" });
 *
 * All coordinates in the JSON are in slide pixels (data.canvas.width x height);
 * boxes are positioned by their centre (x, y).
 */
(function (global) {
  const GREEN = "#548235", GREY = "#7f7f7f", BLUE = "#009dff", ARROW = "#335fa8";
  const BOX_FILL = "#729fcf", BOX_STROKE = "#335fa8";

  // Wrap text into <tspan> lines that fit `maxWidth`.
  function wrap(text, words, maxWidth, lineHeight, x) {
    const el = text.node();
    let line = [], lineNo = 0;
    const startY = text.attr("y") || 0;
    let tspan = text.text(null).append("tspan").attr("x", x).attr("y", startY);
    words.forEach(function (w) {
      line.push(w);
      tspan.text(line.join(" "));
      if (line.length > 1 && tspan.node().getComputedTextLength() > maxWidth) {
        line.pop();
        tspan.text(line.join(" "));
        line = [w];
        lineNo++;
        tspan = text.append("tspan").attr("x", x).attr("y", +startY + lineNo * lineHeight).text(w);
      }
    });
    return lineNo + 1;
  }

  // Point where the ray from rect centre towards (tx,ty) leaves the rectangle.
  function edgePoint(b, tx, ty, pad) {
    const dx = tx - b.x, dy = ty - b.y;
    const hw = b.width / 2 + pad, hh = b.height / 2 + pad;
    const s = 1 / Math.max(Math.abs(dx) / hw, Math.abs(dy) / hh);
    return [b.x + dx * s, b.y + dy * s];
  }

  function draw(container, data, opts) {
    opts = opts || {};
    const W = data.canvas.width, H = data.canvas.height;
    const root = d3.select(container);
    root.selectAll("*").remove();
    const svg = root.append("svg")
      .attr("viewBox", [0, 0, W, H].join(" "))
      .attr("class", "learning-path")
      .attr("role", "img")
      .attr("aria-label", data.title || "Learning path");

    svg.append("defs").append("marker")
      .attr("id", "lp-arrowhead").attr("viewBox", "0 0 10 10")
      .attr("refX", 9).attr("refY", 5).attr("markerWidth", 7).attr("markerHeight", 7)
      .attr("orient", "auto-start-reverse").attr("markerUnits", "userSpaceOnUse")
      .append("path").attr("d", "M0,0 L10,5 L0,10 z").attr("fill", ARROW);

    svg.append("rect").attr("width", W).attr("height", H).attr("fill", "#fff");

    if (opts.background) {
      svg.append("image").attr("href", opts.background).attr("width", W).attr("height", H)
        .attr("opacity", opts.backgroundOpacity == null ? 0.5 : opts.backgroundOpacity);
    }

    const bottom = d3.max(data.levels, (l) => l.yEnd);
    const sectionById = new Map(data.sections.map((s) => [s.id, s]));

    // ---- section columns -------------------------------------------------
    const secs = svg.append("g").attr("class", "sections")
      .selectAll("g").data(data.sections).join("g").attr("class", "section");
    secs.append("rect")
      .attr("x", (d) => d.x).attr("y", 14).attr("width", (d) => d.width)
      .attr("height", bottom - 14).attr("fill", (d) => d.color);
    secs.append("text").attr("class", "section-label")
      .attr("x", (d) => d.x + d.width / 2).attr("y", 36)
      .attr("text-anchor", "middle").text((d) => d.label);

    // ---- Bloom's levels column (left) ------------------------------------
    const left = svg.append("g").attr("class", "bloom");
    if (data.bloom && data.bloom.title) {
      const t = left.append("text").attr("class", "bloom-title").attr("text-anchor", "middle")
        .attr("x", data.bloom.x || 88);
      data.bloom.title.forEach(function (line, i) {
        t.append("tspan").attr("x", data.bloom.x || 88).attr("y", 38 + i * 28)
          .attr("class", i === data.bloom.title.length - 1 ? "bloom-title-last" : null).text(line);
      });
    }
    const leftX = 16, leftW = 148, lh = 19.5;
    data.levels.forEach(function (lvl, i) {
      let y = lvl.bloomY != null ? lvl.bloomY : lvl.yStart + 24;
      const x = i === 0 ? leftX : leftX + 6;
      (lvl.bloom || []).forEach(function (b) {
        left.append("text").attr("class", "bloom-term").attr("x", x).attr("y", y).text(b.term);
        y += lh;
        const t = left.append("text").attr("class", "bloom-text").attr("x", x).attr("y", y);
        const n = wrap(t, b.text.split(/\s+/), leftW - (x - leftX), lh, x);
        y += n * lh + 3;
      });
    });

    // ---- Stages column (right) -------------------------------------------
    const right = svg.append("g").attr("class", "stages");
    right.append("text").attr("class", "stages-title").attr("x", 1562).attr("y", 40)
      .attr("text-anchor", "middle").text(data.stagesTitle || "Stages");
    const rightX = 1639, rightW = 156;
    data.levels.forEach(function (lvl) {
      const t = right.append("text").attr("class", "stage-text").attr("text-anchor", "end")
        .attr("y", lvl.descY != null ? lvl.descY : lvl.yStart + 24).attr("x", rightX);
      wrap(t, lvl.description.split(/\s+/), rightW, 19.5, rightX);
    });

    // ---- level separators --------------------------------------------------
    const lines = svg.append("g").attr("class", "levels");
    data.levels.forEach(function (lvl) {
      lines.append("line").attr("x1", 20).attr("x2", 1615).attr("y1", lvl.yEnd).attr("y2", lvl.yEnd)
        .attr("stroke", BLUE).attr("stroke-width", 4);
      lines.append("text").attr("class", "level-label").attr("x", 1615).attr("y", lvl.yEnd - 14)
        .attr("text-anchor", "end").text(lvl.label);
    });

    // ---- arrows ----------------------------------------------------------
    const boxById = new Map(data.boxes.map((b) => [b.id, b]));
    const arrows = svg.append("g").attr("class", "arrows");
    (data.arrows || []).forEach(function (a) {
      const f = boxById.get(a.from), t = boxById.get(a.to);
      if (!f || !t) { console.warn("Unknown box in arrow", a); return; }
      const via = a.via || [];
      const first = via[0] || [t.x, t.y], last = via[via.length - 1] || [f.x, f.y];
      const pts = [edgePoint(f, first[0], first[1], 0)].concat(via, [edgePoint(t, last[0], last[1], 3)]);
      arrows.append("path").attr("class", "arrow")
        .attr("d", d3.line()(pts)).attr("fill", "none").attr("stroke", ARROW)
        .attr("stroke-width", 3).attr("stroke-linejoin", "round")
        .attr("marker-end", "url(#lp-arrowhead)")
        .append("title").text(f.label + " → " + t.label);
    });

    // ---- boxes -----------------------------------------------------------
    const boxes = svg.append("g").attr("class", "boxes")
      .selectAll("g").data(data.boxes).join("g").attr("class", "box")
      .attr("data-section", (d) => d.section)
      .attr("transform", (d) => `translate(${d.x - d.width / 2},${d.y - d.height / 2})`);
    boxes.each(function (d) {
      const g = d3.select(this);
      const link = d.url ? g.append("a").attr("href", d.url) : g;
      link.append("rect").attr("width", d.width).attr("height", d.height)
        .attr("fill", d.fill || BOX_FILL).attr("stroke", BOX_STROKE).attr("stroke-width", 1.5);
      const fs = d.fontSize || 30;
      const t = link.append("text").attr("class", "box-label").style("font-size", fs + "px")
        .attr("text-anchor", "middle").attr("x", d.width / 2).attr("y", 0);
      const n = wrap(t, d.label.split(/\s+/), d.width - 16, fs * 1.12, d.width / 2);
      const total = (n - 1) * fs * 1.12;
      t.selectAll("tspan").attr("y", function (_, i) { return d.height / 2 - total / 2 + i * fs * 1.12 + fs * 0.35; });
      if (d.tooltip) link.append("title").text(d.tooltip);
    });
    return svg;
  }

  function render(container, source, opts) {
    const done = (data) => draw(container, data, opts);
    if (typeof source === "string") {
      return fetch(source).then((r) => {
        if (!r.ok) throw new Error("Cannot load " + source);
        return r.json();
      }).then(done);
    }
    return Promise.resolve(done(source));
  }

  global.LearningPath = { render: render, draw: draw };
})(window);
