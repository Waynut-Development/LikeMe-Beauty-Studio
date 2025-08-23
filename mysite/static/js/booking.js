document.addEventListener("DOMContentLoaded", function () {
  const dateInput = document.getElementById("date");
  const timeSelect = document.getElementById("time");

  dateInput.addEventListener("change", async function () {
    const date = this.value;
    const res = await fetch(`/free_slots/${date}`);
    const times = await res.json();

    timeSelect.innerHTML =
      '<option value="" disabled selected>Выберите время</option>';
    times.forEach((t) => {
      const opt = document.createElement("option");
      opt.value = t;
      opt.textContent = t;
      timeSelect.appendChild(opt);
    });
  });
});
