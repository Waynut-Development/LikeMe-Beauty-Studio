const tableContainer = document.getElementById("table-container");
const statusButtons = document.querySelectorAll(".status-btn");
const navButtons = document.querySelectorAll(".nav-btn");
const dateRangeEl = document.getElementById("date-range");
const periodButtons = document.querySelectorAll(".period-btn");

// Функция для установки режима в зависимости от ширины
function setPeriodByWidth() {
  const width = window.innerWidth;
  let targetPeriod = width < 768 ? "day" : "week";

  periodButtons.forEach((btn) => {
    btn.classList.remove("active");
    if (btn.dataset.period === targetPeriod) {
      btn.classList.add("active");
    }
  });

  loadSchedule(targetPeriod);
}

// Следим за ресайзом
window.addEventListener("resize", setPeriodByWidth);

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
  function formatDateDots(d) {
    // Форматируем дату в dd.mm.yyyy для отображения
    const day = String(d.getDate()).padStart(2, "0");
    const month = String(d.getMonth() + 1).padStart(2, "0");
    const year = d.getFullYear();
    return `${day}.${month}.${year}`;
  }

  if (dates.length === 1) {
    dateRangeEl.textContent = formatDateDots(dates[0]);
  } else {
    dateRangeEl.textContent = `${formatDateDots(dates[0])} — ${formatDateDots(
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

    // Определяем режим: закрашивать или стирать
    paintMode = cell.classList.contains(currentStatus) ? "erase" : "apply";
    painting = true;

    if (paintMode === "apply") applyStatus(cell);
    else eraseStatus(cell);

    e.preventDefault();
  }

  function handlePointerMove(e) {
    if (!painting) return;
    const cell = e.target.closest("td.paintable");
    if (!cell) return;

    if (paintMode === "apply") applyStatus(cell);
    else eraseStatus(cell);
  }

  function handlePointerUp() {
    painting = false;
  }

  // навешиваем события
  tableEl.addEventListener("pointerdown", handlePointerDown);
  tableEl.addEventListener("pointermove", handlePointerMove);
  window.addEventListener("pointerup", handlePointerUp);
}

// ---------- ГЕНЕРАЦИЯ ТАБЛИЦЫ ----------
function generateTable(dates, times, data) {
  setDateRangeText(dates);

  let html = '<table><thead><tr><th class="time-cell"></th>';
  dates.forEach((d) => {
    // Для отображения пользователю — dd.mm
    const day = String(d.getDate()).padStart(2, "0");
    const month = String(d.getMonth() + 1).padStart(2, "0");
    html += `<th>${day}.${month}</th>`;
  });
  html += "</tr></thead><tbody>";

  times.forEach((time) => {
    html += `<tr><td class="time-cell">${time}</td>`;
    dates.forEach((date) => {
      const dateStr = formatDate(date); // остаётся yyyy-mm-dd для data-date
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
setPeriodByWidth();

const defaultStatusBtn = document.querySelector('.status-btn[data-status="busy"]');
if (defaultStatusBtn) {
  statusButtons.forEach((b) => b.classList.remove("active"));
  defaultStatusBtn.classList.add("active");
  currentStatus = "busy";
}