function setTargetToEnglish() {
  document.getElementById('targetLanguage').value = 'English';
}

function calculateTotal() {
  const pageCount = parseInt(document.getElementById('pageCount').value) || 0;
  const total = (pageCount * 1.95).toFixed(2);

  document.getElementById('totalCost').innerText = `$${total}`;
  document.getElementById('pageSummary').innerText = `${pageCount} page${pageCount !== 1 ? 's' : ''}`;

  const source = document.getElementById('sourceLanguage').value;
  const target = document.getElementById('targetLanguage').value;

  if (source && target) {
    document.getElementById('selectedLanguages').innerText = `${capitalize(source)} → ${capitalize(target)}`;
  } else {
    document.getElementById('selectedLanguages').innerText = 'No languages selected';
  }
}

function capitalize(str) {
  return str.charAt(0).toUpperCase() + str.slice(1).toLowerCase();
}

function handleFiles(files) {
  const estimatedPages = files.length;
  document.getElementById("pageCount").value = estimatedPages;
  calculateTotal();

  const fileListEl = document.getElementById("fileList");
  fileListEl.innerHTML = "";

  const uploadedFileNames = [];

  Array.from(files).forEach((file, index) => {
    uploadedFileNames.push(file.name);

    const li = document.createElement("li");
    li.className = "file-item";

    const number = document.createElement("span");
    number.className = "file-number";
    number.textContent = `${index + 1}.`;

    const link = document.createElement("a");
    link.href = URL.createObjectURL(file);
    link.textContent = file.name;
    link.target = "_blank";
    link.className = "file-link";

    li.appendChild(number);
    li.appendChild(link);
    fileListEl.appendChild(li);
  });

  // Сохраняем имена в localStorage (можно использовать потом)
  localStorage.setItem("uploadedFileNames", JSON.stringify(uploadedFileNames));
}

document.addEventListener("DOMContentLoaded", () => {
  const fileInput = document.getElementById("documentUpload");
  const uploadBox = document.querySelector(".upload-box");

  fileInput.addEventListener("change", () => {
    handleFiles(fileInput.files);
  });

  uploadBox.addEventListener("dragover", (e) => {
    e.preventDefault();
    uploadBox.classList.add("dragging");
  });

  uploadBox.addEventListener("dragleave", () => {
    uploadBox.classList.remove("dragging");
  });

  uploadBox.addEventListener("drop", (e) => {
    e.preventDefault();
    uploadBox.classList.remove("dragging");

    const droppedFiles = e.dataTransfer.files;
    fileInput.files = droppedFiles;
    handleFiles(droppedFiles);
  });

  document.getElementById("pageCount").addEventListener("input", calculateTotal);
  document.getElementById("sourceLanguage").addEventListener("change", () => {
    setTargetToEnglish();
    calculateTotal();
  });

  calculateTotal();
});

["dragover", "drop"].forEach(event => {
  window.addEventListener(event, e => e.preventDefault());
});

function goToOptions() {
  const pageCount = document.getElementById("pageCount").value;
  const sourceLang = document.getElementById("sourceLanguage").value;
  const targetLang = document.getElementById("targetLanguage").value;
  const total = document.getElementById("totalCost").textContent;
  const files = document.getElementById("documentUpload").files;

  if (!sourceLang || files.length === 0) {
    alert("Please select a source language and upload at least one document.");
    return;
  }

  localStorage.setItem("pageCount", pageCount);
  localStorage.setItem("sourceLanguage", sourceLang);
  localStorage.setItem("targetLanguage", targetLang);
  localStorage.setItem("totalCost", total);

  // Переход
  window.location.href = "/options";
}
