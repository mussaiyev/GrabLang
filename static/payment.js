document.addEventListener("DOMContentLoaded", () => {
  const fullName = document.getElementById("fullName");
  const emailInput = document.getElementById("email");
  const placeOrderBtn = document.getElementById("placeOrder");

  // Получаем данные из localStorage
  const sourceLang = localStorage.getItem("finalSourceLang") || localStorage.getItem("sourceLanguage") || "Unknown";
  const targetLang = localStorage.getItem("finalTargetLang") || "English";
  const pageCount = localStorage.getItem("finalPageCount") || localStorage.getItem("pageCount") || "0";
  const total = localStorage.getItem("finalTotal") || "$0.00";
  const turnaround = localStorage.getItem("finalTurnaround") || "24 hours";
  const addons = JSON.parse(localStorage.getItem("finalAddons") || "[]");

  // Обновление информации на странице
  document.getElementById("langSummary").textContent = `${sourceLang} to ${targetLang}`;
  document.getElementById("pageSummary").textContent = `${pageCount} page${pageCount !== "1" ? "s" : ""}`;
  document.getElementById("totalCost").textContent = total;
  document.getElementById("turnaround").textContent = turnaround;

  const addonsList = document.getElementById("addonsList");
  addonsList.innerHTML = "";
  addons.forEach(service => {
    const item = document.createElement("p");
    item.textContent = service;
    addonsList.appendChild(item);
  });

  // Заполнение скрытых полей формы
  document.getElementById("hiddenSourceLang").value = sourceLang;
  document.getElementById("hiddenTargetLang").value = targetLang;
  document.getElementById("hiddenPageCount").value = pageCount;
  document.getElementById("hiddenAddons").value = addons.join(", ");
  document.getElementById("hiddenTotal").value = total;

  // Валидация email
  const errorIcon = document.getElementById("emailErrorIcon");
  const errorText = document.getElementById("emailErrorText");

  function isValidEmail(email) {
    return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email);
  }

  placeOrderBtn.addEventListener("click", (e) => {
    const emailValue = emailInput.value.trim();
    const nameValue = fullName.value.trim();

    if (!nameValue || !isValidEmail(emailValue)) {
      e.preventDefault();
      emailInput.classList.add("error");
      errorIcon.style.display = "inline";
      errorText.style.display = "block";
    } else {
      emailInput.classList.remove("error");
      errorIcon.style.display = "none";
      errorText.style.display = "none";
    }
  });
});
