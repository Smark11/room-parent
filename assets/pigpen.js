/* Pigpen cipher renderer, shared by the Halloween page and the printables. */
// ---- Pigpen cipher renderer ----
// Standard Pigpen: A–I tic-tac-toe grid, J–R same grid with a dot,
// S–V the X, W–Z the X with a dot.
(function () {
  const els = document.querySelectorAll(".pigpen[data-text]");
  if (!els.length) return;
  const GRID = "ABCDEFGHIJKLMNOPQR", X = "STUVWXYZ";
  const S = 26, m = 4, M = S - m, c = S / 2;
  function gridGlyph(i, dot) {
    const r = Math.floor(i / 3), col = i % 3;
    const lines = [];
    if (col < 2) lines.push([M, m, M, M]);      // right side
    if (col > 0) lines.push([m, m, m, M]);      // left side
    if (r < 2) lines.push([m, M, M, M]);        // bottom
    if (r > 0) lines.push([m, m, M, m]);        // top
    return svg(lines, dot ? [c, c] : null);
  }
  function xGlyph(i, dot) {
    // 0 top (V), 1 left (>), 2 right (<), 3 bottom (^)
    const TL = [m, m], TR = [M, m], BL = [m, M], BR = [M, M], C = [c, c];
    const pairs = [[TL, TR], [TL, BL], [TR, BR], [BL, BR]][i];
    const lines = pairs.map(p => [C[0], C[1], p[0], p[1]]);
    const dots = [[c, m + 5], [m + 5, c], [M - 5, c], [c, M - 5]][i];
    return svg(lines, dot ? dots : null);
  }
  function svg(lines, dot) {
    return `<svg viewBox="0 0 ${S} ${S}" width="${S}" height="${S}" aria-hidden="true">` +
      lines.map(l => `<line x1="${l[0]}" y1="${l[1]}" x2="${l[2]}" y2="${l[3]}" stroke="currentColor" stroke-width="2.4" stroke-linecap="round"/>`).join("") +
      (dot ? `<circle cx="${dot[0]}" cy="${dot[1]}" r="2.6" fill="currentColor"/>` : "") + `</svg>`;
  }
  function glyph(ch) {
    let i = GRID.indexOf(ch);
    if (i >= 0) return gridGlyph(i % 9, i >= 9);
    i = X.indexOf(ch);
    if (i >= 0) return xGlyph(i % 4, i >= 4);
    return null;
  }
  els.forEach(el => {
    const words = el.dataset.text.toUpperCase().split(/\s+/);
    el.innerHTML = words.map(w => `<span class="pp-word">` +
      w.split("").map(ch => { const g = glyph(ch); return g ? `<span class="pp-g" title="">${g}</span>` : `<span class="pp-txt">${ch}</span>`; }).join("") +
      `</span>`).join(" ");
  });
  document.querySelectorAll("[data-pigpen-key]").forEach(el => {
    el.innerHTML = "ABCDEFGHIJKLMNOPQRSTUVWXYZ".split("").map(ch =>
      `<span class="pp-key-item"><span class="pp-g">${glyph(ch)}</span><b>${ch}</b></span>`).join("");
  });
})();
