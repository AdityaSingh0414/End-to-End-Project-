const form = document.getElementById("prediction-form");
const resultCard = document.getElementById("result-card");
const reportCard = document.getElementById("report-card");
const uploadForm = document.getElementById("upload-form");
const uploadPreview = document.getElementById("upload-preview");
const historyList = document.getElementById("history-list");

function escapeHtml(value) {
  return String(value)
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#39;");
}

function riskClass(level) {
  return `risk-${String(level || "").toLowerCase()}`;
}

function renderResult(data) {
  resultCard.classList.remove("empty");
  resultCard.innerHTML = `
    <div class="risk-badge ${riskClass(data.risk_level)}">${escapeHtml(data.risk_level)} Risk</div>
    <div class="score">${(Number(data.risk_score) * 100).toFixed(1)}%</div>
    <p><strong>${escapeHtml(data.patient_name)}</strong> received prediction ID <strong>#${data.prediction_id}</strong>.</p>
    <ul class="list">
      ${data.recommendations.map((item) => `<li>${escapeHtml(item)}</li>`).join("")}
    </ul>
  `;
}

function renderReport(report) {
  reportCard.innerHTML = `
    <h3>Generated Clinical Summary</h3>
    <p>${escapeHtml(report.summary)}</p>
    <ul class="list">
      ${report.clinical_flags.map((item) => `<li>${escapeHtml(item)}</li>`).join("")}
    </ul>
    <p class="muted">${escapeHtml(report.disclaimer)}</p>
  `;
}

async function loadHistory() {
  try {
    const response = await fetch("/api/history");
    const items = await response.json();
    if (!items.length) {
      historyList.textContent = "No predictions yet. Run your first assessment.";
      return;
    }

    historyList.innerHTML = items
      .slice(0, 8)
      .map(
        (item) => `
          <article class="history-item">
            <strong>${escapeHtml(item.patient_name)}</strong>
            <div>${escapeHtml(item.risk_level)} risk • Score ${(Number(item.risk_score) * 100).toFixed(1)}%</div>
            <small>${new Date(item.created_at).toLocaleString()}</small>
          </article>
        `
      )
      .join("");
  } catch (error) {
    historyList.textContent = "Unable to load history right now.";
  }
}

form.addEventListener("submit", async (event) => {
  event.preventDefault();

  const formData = new FormData(form);
  const payload = {
    patient_name: formData.get("patient_name"),
    age: Number(formData.get("age")),
    gender: formData.get("gender"),
    glucose_level: Number(formData.get("glucose_level")),
    blood_pressure: Number(formData.get("blood_pressure")),
    cholesterol: Number(formData.get("cholesterol")),
    bmi: Number(formData.get("bmi")),
    symptom_severity: Number(formData.get("symptom_severity")),
    activity_level: Number(formData.get("activity_level")),
    has_diabetes_history: formData.get("has_diabetes_history") === "on",
    has_hypertension_history: formData.get("has_hypertension_history") === "on",
    notes: formData.get("notes"),
  };

  resultCard.classList.remove("empty");
  resultCard.innerHTML = "<p>Running healthcare AI prediction...</p>";
  reportCard.innerHTML = "";

  try {
    const response = await fetch("/api/predict", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });

    if (!response.ok) {
      throw new Error("Prediction request failed");
    }

    const prediction = await response.json();
    renderResult(prediction);

    const reportResponse = await fetch(`/api/report/${prediction.prediction_id}`);
    const report = await reportResponse.json();
    renderReport(report);
    loadHistory();
  } catch (error) {
    resultCard.innerHTML = "<p>Prediction failed. Please verify the backend is running.</p>";
  }
});

uploadForm.addEventListener("submit", async (event) => {
  event.preventDefault();
  const fileInput = document.getElementById("patient-file");
  if (!fileInput.files.length) {
    return;
  }

  const data = new FormData();
  data.append("file", fileInput.files[0]);
  uploadPreview.textContent = "Parsing upload...";

  try {
    const response = await fetch("/api/upload", {
      method: "POST",
      body: data,
    });
    const result = await response.json();
    const headers = Object.keys(result.preview[0] || {});
    if (!result.preview.length) {
      uploadPreview.textContent = "No rows detected in the uploaded file.";
      return;
    }

    uploadPreview.innerHTML = `
      <p>Parsed <strong>${result.records}</strong> records from <strong>${escapeHtml(result.filename)}</strong>.</p>
      <table>
        <thead>
          <tr>${headers.map((header) => `<th>${escapeHtml(header)}</th>`).join("")}</tr>
        </thead>
        <tbody>
          ${result.preview
            .map(
              (row) => `
                <tr>${headers.map((header) => `<td>${escapeHtml(row[header])}</td>`).join("")}</tr>
              `
            )
            .join("")}
        </tbody>
      </table>
    `;
  } catch (error) {
    uploadPreview.textContent = "Upload preview failed.";
  }
});

loadHistory();
