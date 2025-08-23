const tableContainer = document.getElementById("table-container");
const periodButtons = document.querySelectorAll(".period-btn");
const statusButtons = document.querySelectorAll(".status-btn");
const navButtons = document.querySelectorAll(".nav-btn");
const dateRangeEl = document.getElementById("date-range");

let currentStatus = null;
let startDate = new Date();
startDate.setHours(0, 0, 0, 0);

let painting = false;
let paintMode = "apply";

// ---------- ВРЕМЕНА ----------
function getTimes() {
  const times = [];
  for (let h = 7; h < 24; h++) {
    times.push(`${String(h).padStart(2, "0")}:00`);
    times.push(`${String(h).padStart(2, "0")}:30`);
  }
  for (let h = 0; h < 2; h++) {
    times.push(`${String(h).padStart(2, "0")}:00`);
    times.push(`${String(h).padStart(2, "0")}:30`);
  }
  times.push("02:00");
  return times;
}

function formatDate(d) {
  return d.toISOString().slice(0, 10); // yyyy-mm-dd
}

function getDates(period) {
  const base = new Date(startDate);
  base.setHours(0, 0, 0, 0);
  if (period === "day") return [base];
  return Array.from({ length: 7 }, (_, i) => {
    const d = new Date(base);
    d.setDate(base.getDate() + i);
    return d;
  });
}

function setDateRangeText(dates) {
  if (dates.length === 1) {
    dateRangeEl.textContent = formatDate(dates[0]);
  } else {
    dateRangeEl.textContent = `${formatDate(dates[0])} — ${formatDate(
      dates[dates.length - 1]
    )}`;
  }
}

// ---------- СТАТУСЫ ----------
function clearStatuses(cell) {
  cell.classList.remove("free", "busy", "off");
}
function applyStatus(cell) {
  if (!currentStatus) return;
  clearStatuses(cell);
  cell.classList.add(currentStatus);
}
function eraseStatus(cell) {
  clearStatuses(cell);
}
function toggleOnce(cell) {
  if (!currentStatus) return;
  if (cell.classList.contains(currentStatus)) eraseStatus(cell);
  else applyStatus(cell);
}

// ---------- РИСОВАНИЕ ----------
function attachPaintHandlers(tableEl) {
  const cells = tableEl.querySelectorAll("td.paintable");

  function handlePointerDown(e) {
    const cell = e.target.closest("td.paintable");
    if (!cell || !currentStatus) return;
    paintMode = cell.classList.contains(currentStatus) ? "erase" : "apply";
    painting = true;
    if (paintMode === "apply") applyStatus(cell);
    else eraseStatus(cell);
    cell.setPointerCapture?.(e.pointerId);
    e.preventDefault();
  }

  function handlePointerEnter(e) {
    if (!painting) return;
    const cell = e.target.closest("td.paintable");
    if (!cell) return;
    if (paintMode === "apply") applyStatus(cell);
    else eraseStatus(cell);
  }

  function handlePointerOver(e) {
    if (!painting) return;
    const cell = e.target.closest("td.paintable");
    if (!cell) return;
    if (paintMode === "apply") applyStatus(cell);
    else eraseStatus(cell);
  }

  function handlePointerUp() {
    painting = false;
  }

  tableEl.addEventListener("pointerdown", handlePointerDown);
  tableEl.addEventListener("pointerenter", handlePointerEnter, true);
  tableEl.addEventListener("pointerover", handlePointerOver, true);
  window.addEventListener("pointerup", handlePointerUp);
}

// ---------- ГЕНЕРАЦИЯ ТАБЛИЦЫ ----------
function generateTable(dates, times, data) {
  setDateRangeText(dates);

  let html = '<table><thead><tr><th class="time-cell">Время</th>';
  dates.forEach((d) => {
    html += `<th>${formatDate(d)}</th>`;
  });
  html += "</tr></thead><tbody>";

  times.forEach((time) => {
    html += `<tr><td class="time-cell">${time}</td>`;
    dates.forEach((date) => {
      const dateStr = formatDate(date);
      const cellData = data.find((d) => d.date === dateStr && d.time === time);
      const status = cellData ? cellData.status : "";
      html += `<td class="paintable ${status}" data-date="${dateStr}" data-time="${time}"></td>`;
    });
    html += "</tr>";
  });

  html += "</tbody></table>";
  tableContainer.innerHTML = html;

  const tableEl = tableContainer.querySelector("table");
  attachPaintHandlers(tableEl);

  tableEl.addEventListener("click", (e) => {
    const cell = e.target.closest("td.paintable");
    if (!cell) return;
    toggleOnce(cell);
  });
}

// ---------- БЭКЕНД ----------
async function loadSchedule(period = "day") {
  const res = await fetch("/schedule");
  const data = await res.json();
  const dates = getDates(period);
  const times = getTimes();
  generateTable(dates, times, data);
}

async function saveSchedule() {
  const cells = [];
  document.querySelectorAll("td.paintable").forEach((cell) => {
    let status = "";
    if (cell.classList.contains("free")) status = "free";
    if (cell.classList.contains("busy")) status = "busy";
    if (cell.classList.contains("off")) status = "off";
    if (status)
      cells.push({
        date: cell.dataset.date,
        time: cell.dataset.time,
        status,
      });
  });
  await fetch("/schedule", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(cells),
  });
  alert("Расписание сохранено!");
}

// ---------- КНОПКИ ----------
periodButtons.forEach((btn) => {
  btn.addEventListener("click", () => {
    periodButtons.forEach((b) => b.classList.remove("active"));
    btn.classList.add("active");
    const period = btn.dataset.period;
    loadSchedule(period);
  });
});

statusButtons.forEach((btn) => {
  btn.addEventListener("click", () => {
    statusButtons.forEach((b) => b.classList.remove("active"));
    btn.classList.add("active");
    currentStatus = btn.dataset.status;
  });
});

navButtons.forEach((btn) => {
  btn.addEventListener("click", () => {
    const period = document.querySelector(".period-btn.active").dataset.period;
    const shift = period === "day" ? 1 : 7;
    const dir = btn.dataset.dir === "next" ? 1 : -1;
    startDate.setDate(startDate.getDate() + dir * shift);
    loadSchedule(period);
  });
});

document.querySelector(".save-btn").addEventListener("click", saveSchedule);

// ---------- СТАРТ ----------
loadSchedule("day");
