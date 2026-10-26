/* =====================================================
   Room Parent HQ — shared behavior
   Edit CONFIG to personalize every page at once.
   ===================================================== */
const CONFIG = {
  className: "Room 12",             // e.g. "Room 12" or "Ms. Rivera's Class"
  teacherName: "Ms. Rivera",        // teacher's name as kids say it
  grade: "4th Grade",
  school: "Maple Hill Elementary",
  roomParentName: "Mark",           // your first name
  studentCount: 20,
  nextEventName: "Halloween Party",
  nextEventDate: "2026-10-30T13:30:00", // local time, ISO format; drives the countdown
  nextEventDisplayDate: "Friday, Oct 30 · 1:30–3:00 PM",
  contactEmail: "roomparent@example.com",
};

// ---- Fill in any element with data-config="key" ----
document.querySelectorAll("[data-config]").forEach(el => {
  const key = el.getAttribute("data-config");
  if (CONFIG[key] !== undefined) el.textContent = CONFIG[key];
});

// ---- Mobile nav ----
const toggle = document.querySelector(".nav-toggle");
const links = document.querySelector(".nav-links");
if (toggle && links) {
  toggle.addEventListener("click", () => {
    const open = links.classList.toggle("open");
    toggle.setAttribute("aria-expanded", String(open));
  });
}

// ---- Theme toggle (light/dark) ----
const themeBtn = document.querySelector(".theme-toggle");
function applyTheme(t) {
  if (t) document.documentElement.setAttribute("data-theme", t);
  else document.documentElement.removeAttribute("data-theme");
  if (themeBtn) themeBtn.textContent = (t === "dark" || (!t && matchMedia("(prefers-color-scheme: dark)").matches)) ? "☀️" : "🌙";
}
try { applyTheme(localStorage.getItem("theme")); } catch (e) { applyTheme(null); }
if (themeBtn) {
  themeBtn.addEventListener("click", () => {
    const isDark = document.documentElement.getAttribute("data-theme") === "dark" ||
      (!document.documentElement.getAttribute("data-theme") && matchMedia("(prefers-color-scheme: dark)").matches);
    const next = isDark ? "light" : "dark";
    try { localStorage.setItem("theme", next); } catch (e) {}
    applyTheme(next);
  });
}

// ---- Countdown ----
const cd = document.querySelector("[data-countdown]");
if (cd) {
  const target = new Date(CONFIG.nextEventDate).getTime();
  const units = { days: cd.querySelector("[data-days]"), hours: cd.querySelector("[data-hours]"), mins: cd.querySelector("[data-mins]"), secs: cd.querySelector("[data-secs]") };
  const tick = () => {
    let diff = Math.max(0, target - Date.now());
    const d = Math.floor(diff / 864e5); diff -= d * 864e5;
    const h = Math.floor(diff / 36e5); diff -= h * 36e5;
    const m = Math.floor(diff / 6e4); diff -= m * 6e4;
    const s = Math.floor(diff / 1e3);
    units.days.textContent = d; units.hours.textContent = String(h).padStart(2, "0");
    units.mins.textContent = String(m).padStart(2, "0"); units.secs.textContent = String(s).padStart(2, "0");
  };
  tick(); setInterval(tick, 1000);
}

// ---- Persistent checklists ----
document.querySelectorAll(".checklist[data-key]").forEach(list => {
  const key = "checklist:" + list.dataset.key;
  const boxes = list.querySelectorAll("input[type=checkbox]");
  const bar = list.previousElementSibling && list.previousElementSibling.classList.contains("checklist-progress")
    ? list.previousElementSibling.firstElementChild : null;
  let saved = {};
  try { saved = JSON.parse(localStorage.getItem(key) || "{}"); } catch (e) {}
  const update = () => {
    const state = {}; let done = 0;
    boxes.forEach((b, i) => { state[i] = b.checked; if (b.checked) done++; });
    try { localStorage.setItem(key, JSON.stringify(state)); } catch (e) {}
    if (bar) bar.style.width = (boxes.length ? (done / boxes.length) * 100 : 0) + "%";
    const counter = list.parentElement.querySelector("[data-checklist-count]");
    if (counter) counter.textContent = `${done} / ${boxes.length}`;
  };
  boxes.forEach((b, i) => { b.checked = !!saved[i]; b.addEventListener("change", update); });
  update();
});
document.querySelectorAll("[data-reset-checklist]").forEach(btn => {
  btn.addEventListener("click", () => {
    const list = document.querySelector(`.checklist[data-key="${btn.dataset.resetChecklist}"]`);
    if (!list) return;
    list.querySelectorAll("input[type=checkbox]").forEach(b => { b.checked = false; b.dispatchEvent(new Event("change")); });
  });
});

// ---- Copy buttons ----
document.querySelectorAll("[data-copy]").forEach(btn => {
  btn.addEventListener("click", async () => {
    const src = document.querySelector(btn.dataset.copy);
    if (!src) return;
    try {
      await navigator.clipboard.writeText(src.innerText);
      const old = btn.textContent; btn.textContent = "Copied ✓";
      setTimeout(() => (btn.textContent = old), 1500);
    } catch (e) { btn.textContent = "Select & copy"; }
  });
});

// ---- Tabs ----
document.querySelectorAll("[data-tabs]").forEach(group => {
  const tabs = group.querySelectorAll("[role=tab]");
  const panels = group.querySelectorAll("[role=tabpanel]");
  tabs.forEach(tab => tab.addEventListener("click", () => {
    tabs.forEach(t => t.setAttribute("aria-selected", "false"));
    panels.forEach(p => (p.hidden = true));
    tab.setAttribute("aria-selected", "true");
    const panel = group.querySelector("#" + tab.getAttribute("aria-controls"));
    if (panel) panel.hidden = false;
  }));
});

// ---- Station rotation timer ----
const timer = document.querySelector("[data-timer]");
if (timer) {
  const digits = timer.querySelector(".digits");
  const label = timer.querySelector(".label");
  const rot = timer.querySelector(".timer-rotation");
  const minutesInput = timer.querySelector("[data-minutes]");
  const stations = JSON.parse(timer.dataset.stations || "[]");
  let round = 0, remaining = 0, handle = null;
  const fmt = s => `${String(Math.floor(s / 60)).padStart(2, "0")}:${String(s % 60).padStart(2, "0")}`;
  const renderRot = () => {
    if (!rot) return;
    rot.innerHTML = stations.map((s, i) => `<span class="${i === round ? "active" : ""}">${s}</span>`).join("");
  };
  const beep = () => {
    try {
      const ctx = new (window.AudioContext || window.webkitAudioContext)();
      [0, 0.25, 0.5].forEach(t => {
        const o = ctx.createOscillator(); const g = ctx.createGain();
        o.frequency.value = 880; o.connect(g); g.connect(ctx.destination);
        g.gain.setValueAtTime(0.3, ctx.currentTime + t); g.gain.exponentialRampToValueAtTime(0.001, ctx.currentTime + t + 0.2);
        o.start(ctx.currentTime + t); o.stop(ctx.currentTime + t + 0.22);
      });
    } catch (e) {}
  };
  const render = () => {
    const shown = (remaining === 0 && handle === null && !timer.classList.contains("done")) ? Math.max(1, parseInt(minutesInput.value || "10", 10)) * 60 : remaining;
    digits.textContent = fmt(shown);
    timer.classList.toggle("warn", remaining <= 60 && remaining > 0);
    timer.classList.toggle("done", remaining === 0 && handle === null && round > 0);
    label.textContent = stations.length ? `Rotation ${Math.min(round + 1, stations.length)} of ${stations.length}` : "Rotation";
    renderRot();
  };
  const start = () => {
    if (handle) return;
    if (remaining === 0) remaining = Math.max(1, parseInt(minutesInput.value || "10", 10)) * 60;
    handle = setInterval(() => {
      remaining--; render();
      if (remaining <= 0) { clearInterval(handle); handle = null; beep(); timer.classList.add("done"); label.textContent = "ROTATE! Agents move to the next station →"; }
    }, 1000);
  };
  const pause = () => { clearInterval(handle); handle = null; };
  const next = () => { pause(); round = (round + 1) % Math.max(1, stations.length); remaining = 0; timer.classList.remove("done"); render(); start(); };
  const reset = () => { pause(); round = 0; remaining = 0; timer.classList.remove("done"); render(); };
  timer.querySelector("[data-start]").addEventListener("click", start);
  timer.querySelector("[data-pause]").addEventListener("click", pause);
  timer.querySelector("[data-next]").addEventListener("click", next);
  timer.querySelector("[data-reset]").addEventListener("click", reset);
  minutesInput.addEventListener("input", () => { if (handle === null) { remaining = 0; render(); } });
  render();
}

// ---- Caesar cipher tool ----
const cipher = document.querySelector("[data-cipher]");
if (cipher) {
  const input = cipher.querySelector("textarea");
  const shift = cipher.querySelector("input[type=range]");
  const shiftVal = cipher.querySelector("[data-shift-val]");
  const out = cipher.querySelector("output");
  const wheel = cipher.querySelector(".cipher-wheel");
  const mode = () => cipher.querySelector("input[name=mode]:checked").value;
  const A = "ABCDEFGHIJKLMNOPQRSTUVWXYZ";
  const run = () => {
    const k = parseInt(shift.value, 10) * (mode() === "decode" ? -1 : 1);
    shiftVal.textContent = shift.value;
    out.textContent = (input.value || "").toUpperCase().split("").map(ch => {
      const i = A.indexOf(ch); if (i < 0) return ch;
      return A[(i + k + 26) % 26];
    }).join("");
    const k2 = parseInt(shift.value, 10);
    wheel.innerHTML = `<div>${A.split("").join(" ")}</div><div style="color:var(--coral-dark)">${A.split("").map((c, i) => A[(i + k2) % 26]).join(" ")}</div>`;
  };
  [input, shift].forEach(el => el.addEventListener("input", run));
  cipher.querySelectorAll("input[name=mode]").forEach(r => r.addEventListener("change", run));
  run();
}

// ---- Budget calculator ----
const budget = document.querySelector("[data-budget]");
if (budget) {
  const rows = budget.querySelectorAll("tr[data-cost]");
  const total = budget.querySelector("[data-total]");
  const perKid = budget.querySelector("[data-per-kid]");
  const update = () => {
    let sum = 0;
    rows.forEach(r => { const box = r.querySelector("input[type=checkbox]"); if (!box || box.checked) sum += parseFloat(r.dataset.cost); });
    total.textContent = "$" + sum.toFixed(0);
    if (perKid) perKid.textContent = "$" + (sum / CONFIG.studentCount).toFixed(2);
  };
  rows.forEach(r => { const box = r.querySelector("input[type=checkbox]"); if (box) box.addEventListener("change", update); });
  update();
}

// ---- Footer year ----
document.querySelectorAll("[data-year]").forEach(el => (el.textContent = new Date().getFullYear()));
