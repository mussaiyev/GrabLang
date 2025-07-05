const basePrice = 1.95;
const notarizationFee = 19.95;
const expeditedFeePerPage = 14.95;

// Получаем данные из localStorage
const pages = parseInt(localStorage.getItem("pageCount")) || 1;
const sourceLang = localStorage.getItem("sourceLanguage") || "Unknown";
const targetLang = localStorage.getItem("targetLanguage") || "English";

function updateSummary() {
  let total = basePrice * pages;
  const addons = [];

  const notarization = document.getElementById("notarization");
  const expedited = document.getElementById("expedited");
  const turnaround = document.getElementById("turnaround");
  const addOnsList = document.getElementById("addOnsList");

  addOnsList.innerHTML = "";

  if (notarization && notarization.checked) {
    total += notarizationFee;
    addons.push("Notarization");
    addOnsList.innerHTML += `<p>✔ Notarization</p>`;
  }

  if (expedited && expedited.checked) {
    total += expeditedFeePerPage * pages;
    addons.push("Expedited Turnaround");
    addOnsList.innerHTML += `<p>✔ Expedited Turnaround</p>`;
    turnaround.textContent = "12–24 hours";
  } else {
    turnaround.textContent = "3–4 days";
  }

  document.getElementById("totalCost").textContent = `$${total.toFixed(2)}`;

  // Обновляем LocalStorage
  localStorage.setItem("notarizationChecked", notarization?.checked);
  localStorage.setItem("expeditedChecked", expedited?.checked);
  localStorage.setItem("finalAddons", JSON.stringify(addons));
  localStorage.setItem("finalTotal", total.toFixed(2));
  localStorage.setItem("finalTurnaround", turnaround.textContent);
}

function saveOrderDataBeforeSubmit() {
  updateSummary(); // обновим на всякий случай

  const addons = JSON.parse(localStorage.getItem("finalAddons") || "[]");
  const total = localStorage.getItem("finalTotal") || "0.00";

  document.getElementById("hiddenAddons").value = addons.join(", ");
  document.getElementById("hiddenTotal").value = `$${total}`;
}

document.addEventListener("DOMContentLoaded", () => {
  // Заполняем языки и страницы
  document.getElementById("languageSummary").textContent = `${sourceLang} to ${targetLang}`;
  document.getElementById("pageSummary").textContent = `${pages} page${pages !== 1 ? "s" : ""}`;

  // Восстанавливаем чекбоксы
  if (localStorage.getItem("notarizationChecked") === "true") {
    document.getElementById("notarization").checked = true;
  }

  if (localStorage.getItem("expeditedChecked") === "true") {
    document.getElementById("expedited").checked = true;
  }

  // Навешиваем обработчики
  document.getElementById("notarization").addEventListener("change", updateSummary);
  document.getElementById("expedited").addEventListener("change", updateSummary);
  document.getElementById("optionsForm").addEventListener("submit", saveOrderDataBeforeSubmit);

  updateSummary();
});
