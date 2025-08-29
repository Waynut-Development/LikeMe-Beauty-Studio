document.addEventListener("DOMContentLoaded", async function () {
  const dateSelect = document.getElementById("date");
  const timeSelect = document.getElementById("time");

  // ======= ПОЛУЧАЕМ СПИСОК ДОСТУПНЫХ ДАТ =======
  let freeDates = [];
  try {
    const res = await fetch("/free_dates");
    freeDates = await res.json(); // ["2025-09-01", "2025-09-05", "2025-09-07"]
  } catch (err) {
    console.error("Ошибка при получении доступных дат:", err);
  }

  // ======= ЗАПОЛНЯЕМ SELECT ДАТ =======
  dateSelect.innerHTML =
    '<option value="" disabled selected>Выберите дату</option>';

  if (freeDates.length > 0) {
    freeDates.forEach((d) => {
      const opt = document.createElement("option");
      opt.value = d; // сохраняем полную дату YYYY-MM-DD (для сервера)

      // показываем пользователю только день и месяц
      const [year, month, day] = d.split("-");
      opt.textContent = `${day}.${month}`;

      dateSelect.appendChild(opt);
    });
  } else {
    const opt = document.createElement("option");
    opt.disabled = true;
    opt.textContent = "Нет доступных дат";
    dateSelect.appendChild(opt);
  }

  // ======= ПОДГРУЗКА ВРЕМЕНИ ДЛЯ ВЫБРАННОЙ ДАТЫ =======
  dateSelect.addEventListener("change", async function () {
    const selectedDate = this.value; // тут остаётся YYYY-MM-DD
    if (!selectedDate) return;

    try {
      const res = await fetch(`/free_slots/${selectedDate}`);
      const times = await res.json();

      timeSelect.innerHTML =
        '<option value="" disabled selected>Выберите время</option>';

      if (times.length > 0) {
        times.forEach((t) => {
          const opt = document.createElement("option");
          opt.value = t;
          opt.textContent = t;
          timeSelect.appendChild(opt);
        });
      } else {
        const opt = document.createElement("option");
        opt.disabled = true;
        opt.textContent = "Нет свободного времени";
        timeSelect.appendChild(opt);
      }
    } catch (err) {
      console.error("Ошибка при получении слотов:", err);
      timeSelect.innerHTML =
        '<option value="" disabled selected>Ошибка загрузки</option>';
    }
  });
});
