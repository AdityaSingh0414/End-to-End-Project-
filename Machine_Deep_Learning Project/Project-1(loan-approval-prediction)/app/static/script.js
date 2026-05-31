/**
 * script.js — LoanAI Frontend Logic
 * Multi-page SPA: Dashboard, Apply Now, Analytics
 * Multi-bank recommendation, chatbot, charts
 */

"use strict";

// ─── State ─────────────────────────────────────────────────────────────────
const state = {
  currentPage: "dashboard",
  metricsData: null,
  featureData: null,
  lastResult: null,
};

// ─── On Load ────────────────────────────────────────────────────────────────
document.addEventListener("DOMContentLoaded", () => {
  initNavigation();
  loadDashboard();
  document.getElementById("loan-form").addEventListener("submit", handleSubmit);
});

// ─── Navigation ─────────────────────────────────────────────────────────────
function initNavigation() {
  document.querySelectorAll(".nav-link").forEach(link => {
    link.addEventListener("click", () => {
      const page = link.dataset.page;
      showPage(page);
    });
  });
}

function showPage(pageId) {
  state.currentPage = pageId;
  // Toggle nav active state
  document.querySelectorAll(".nav-link").forEach(l => l.classList.remove("active"));
  document.querySelector(`.nav-link[data-page="${pageId}"]`)?.classList.add("active");
  // Toggle page visibility
  document.querySelectorAll(".page").forEach(p => p.classList.remove("active"));
  const page = document.getElementById(`page-${pageId}`);
  if (page) {
    page.classList.add("active");
    window.scrollTo({ top: 0, behavior: "smooth" });
  }
  // Lazy-load analytics charts on first visit
  if (pageId === "analytics" && !state.analyticsLoaded) {
    loadAnalytics();
    state.analyticsLoaded = true;
  }
}

// ─── Dashboard Data ─────────────────────────────────────────────────────────
async function loadDashboard() {
  try {
    const [metricsRes, featRes, bankRes] = await Promise.all([
      fetch("/api/metrics"),
      fetch("/api/feature-importance"),
      fetch("/api/banks"),
    ]);

    const metricsJson = await metricsRes.json();
    const featJson    = await featRes.json();
    const bankJson    = await bankRes.json();

    if (metricsJson.status === "success") {
      state.metricsData = metricsJson.data;
      renderMetricCards(state.metricsData);
    } else {
      showMetricsNotReady();
    }

    if (featJson.status === "success") {
      state.featureData = featJson.data;
      renderDashboardFeatureChart(featJson.data.slice(0, 6));
    }

    if (bankJson.status === "success") {
      renderBankOverview(bankJson.data);
    }
  } catch (err) {
    console.warn("Dashboard data unavailable:", err);
    showMetricsNotReady();
  }
}

function showMetricsNotReady() {
  setText("m-accuracy", "N/A");
  setText("m-f1", "N/A");
  setText("m-auc", "N/A");
  setText("m-model", "Not trained");
}

// ─── Metric Cards ────────────────────────────────────────────────────────────
function renderMetricCards(data) {
  const acc = (data.accuracy * 100).toFixed(1) + "%";
  const f1  = (data.f1_score * 100).toFixed(1) + "%";
  const auc = data.roc_auc.toFixed(3);

  animateText("m-accuracy", acc);
  animateText("m-f1", f1);
  animateText("m-auc", auc);
  animateText("m-model", data.model_name || "N/A");

  // Hero stats
  animateText("hero-accuracy", acc);
  animateText("hero-auc", auc);

  setTimeout(() => {
    setBarWidth("bar-accuracy", data.accuracy * 100);
    setBarWidth("bar-f1", data.f1_score * 100);
    setBarWidth("bar-auc", data.roc_auc * 100);
  }, 300);
}

function renderDashboardFeatureChart(data) {
  const ctx = document.getElementById("dashFeatureChart")?.getContext("2d");
  if (!ctx) return;
  const labels = data.map(d => d.feature.replace(/_/g, " "));
  const values = data.map(d => d.importance);
  const grad = ctx.createLinearGradient(0, 0, ctx.canvas.width, 0);
  grad.addColorStop(0, "#3b82f6"); grad.addColorStop(1, "#8b5cf6");

  new Chart(ctx, {
    type: "bar",
    data: { labels, datasets: [{ data: values, backgroundColor: grad, borderRadius: 6, barThickness: 16 }] },
    options: {
      indexAxis: "y", responsive: true, maintainAspectRatio: false,
      animation: { duration: 1200, easing: "easeOutQuart" },
      plugins: { legend: { display: false }, tooltip: { callbacks: { label: c => ` ${(c.raw * 100).toFixed(2)}%` } }},
      scales: {
        x: { grid: { color: "rgba(255,255,255,0.05)" }, ticks: { color: "#94a3b8", font: { size: 11 }, callback: v => (v * 100).toFixed(0) + "%" } },
        y: { grid: { color: "rgba(255,255,255,0.05)" }, ticks: { color: "#94a3b8", font: { size: 11 } } },
      },
    }
  });
}

function renderBankOverview(banks) {
  const grid = document.getElementById("bankOverviewGrid");
  if (!grid) return;
  grid.innerHTML = banks.map(b => `
    <div class="bank-mini-card">
      <h4>${b.name}</h4>
      <div class="bank-meta">
        <span>Min Score <strong>${b.min_credit_score}</strong></span>
        <span>Rate <strong>${b.interest_rate_range[0]}% - ${b.interest_rate_range[1]}%</strong></span>
        <span>Processing <strong>${b.processing_days} days</strong></span>
        <span>Risk <span class="risk-badge risk-${b.risk_tolerance}">${b.risk_tolerance}</span></span>
      </div>
    </div>
  `).join("");
}

// ─── Analytics ──────────────────────────────────────────────────────────────
async function loadAnalytics() {
  try {
    const [metricsRes, featRes] = await Promise.all([
      fetch("/api/metrics"),
      fetch("/api/feature-importance"),
    ]);
    const metricsJson = await metricsRes.json();
    const featJson    = await featRes.json();

    if (metricsJson.status === "success") {
      renderConfusionMatrix(metricsJson.data.confusion_matrix);
      renderCVChart(metricsJson.data.cv_scores);
      renderDonutChart(metricsJson.data);
    }
    if (featJson.status === "success") {
      renderFullFeatureChart(featJson.data);
    }
  } catch (err) {
    console.warn("Analytics data unavailable:", err);
  }
}

function renderConfusionMatrix(cm) {
  if (!cm || cm.length < 2) return;
  const [[tn, fp], [fn, tp]] = cm;
  document.getElementById("confusion-matrix").innerHTML = `
    <div class="cm-table">
      <table>
        <thead><tr><th></th><th>Pred: Rejected</th><th>Pred: Approved</th></tr></thead>
        <tbody>
          <tr>
            <th style="text-align:left;color:#94a3b8;font-size:0.75rem">Actual: Rejected</th>
            <td class="cm-tn">${tn}<br/><span style="font-size:0.65rem;font-weight:400">True Neg</span></td>
            <td class="cm-fp">${fp}<br/><span style="font-size:0.65rem;font-weight:400">False Pos</span></td>
          </tr>
          <tr>
            <th style="text-align:left;color:#94a3b8;font-size:0.75rem">Actual: Approved</th>
            <td class="cm-fn">${fn}<br/><span style="font-size:0.65rem;font-weight:400">False Neg</span></td>
            <td class="cm-tp">${tp}<br/><span style="font-size:0.65rem;font-weight:400">True Pos</span></td>
          </tr>
        </tbody>
      </table>
    </div>`;
}

const CHART_COLORS = {
  bg:  ["rgba(59,130,246,0.7)", "rgba(16,185,129,0.7)", "rgba(139,92,246,0.7)", "rgba(245,158,11,0.7)"],
  bdr: ["#3b82f6", "#10b981", "#8b5cf6", "#f59e0b"],
};

function renderCVChart(cvScores) {
  if (!cvScores) return;
  const ctx = document.getElementById("cvChart")?.getContext("2d");
  if (!ctx) return;
  new Chart(ctx, {
    type: "bar",
    data: {
      labels: Object.keys(cvScores),
      datasets: [{ label: "F1 Score (CV)", data: Object.values(cvScores), backgroundColor: CHART_COLORS.bg, borderColor: CHART_COLORS.bdr, borderWidth: 2, borderRadius: 8, barThickness: 48 }]
    },
    options: {
      responsive: true, maintainAspectRatio: false,
      animation: { duration: 1000, easing: "easeOutBounce" },
      plugins: { legend: { display: false }, tooltip: { callbacks: { label: c => ` ${(c.raw * 100).toFixed(2)}%` } } },
      scales: {
        x: { grid: { display: false }, ticks: { color: "#94a3b8", font: { size: 12 } } },
        y: { beginAtZero: true, max: 1.0, grid: { color: "rgba(255,255,255,0.05)" }, ticks: { color: "#94a3b8", callback: v => (v * 100).toFixed(0) + "%" } },
      },
    }
  });
}

function renderDonutChart(data) {
  const ctx = document.getElementById("donutChart")?.getContext("2d");
  if (!ctx) return;
  const cm = data.confusion_matrix || [[0,0],[0,0]];
  const approved = cm[1][0] + cm[1][1];
  const rejected = cm[0][0] + cm[0][1];
  new Chart(ctx, {
    type: "doughnut",
    data: {
      labels: ["Approved", "Rejected"],
      datasets: [{ data: [approved, rejected], backgroundColor: ["rgba(16,185,129,0.8)", "rgba(244,63,94,0.7)"], borderColor: ["#10b981", "#f43f5e"], borderWidth: 2, hoverOffset: 8 }]
    },
    options: {
      responsive: true, maintainAspectRatio: false, cutout: "65%",
      plugins: { legend: { position: "bottom", labels: { color: "#94a3b8", font: { size: 12 }, padding: 16 } } },
    }
  });
}

function renderFullFeatureChart(data) {
  const ctx = document.getElementById("featFullChart")?.getContext("2d");
  if (!ctx) return;
  const labels = data.map(d => d.feature.replace(/_/g, " "));
  const values = data.map(d => d.importance);
  const grad = ctx.createLinearGradient(0, 0, ctx.canvas.width, 0);
  grad.addColorStop(0, "#3b82f6"); grad.addColorStop(1, "#8b5cf6");
  new Chart(ctx, {
    type: "bar",
    data: { labels, datasets: [{ data: values, backgroundColor: grad, borderRadius: 6, barThickness: 18 }] },
    options: {
      indexAxis: "y", responsive: true, maintainAspectRatio: false,
      animation: { duration: 1200 },
      plugins: { legend: { display: false }, tooltip: { callbacks: { label: c => ` ${(c.raw * 100).toFixed(2)}%` } } },
      scales: {
        x: { grid: { color: "rgba(255,255,255,0.05)" }, ticks: { color: "#94a3b8", callback: v => (v * 100).toFixed(0) + "%" } },
        y: { grid: { color: "rgba(255,255,255,0.05)" }, ticks: { color: "#94a3b8" } },
      },
    }
  });
}

// ═══════════════════════════════════════════════════════════
// APPLY NOW — FORM + MULTI-BANK RECOMMENDATION
// ═══════════════════════════════════════════════════════════

async function handleSubmit(e) {
  e.preventDefault();
  const btn     = document.getElementById("submit-btn");
  const btnText = document.getElementById("btn-text");
  const spinner = document.getElementById("btn-loader");

  btn.disabled = true;
  btnText.classList.add("hidden");
  spinner.classList.remove("hidden");

  const payload = {
    age: parseInt(document.getElementById("f-age").value),
    monthly_income: parseFloat(document.getElementById("f-income").value),
    credit_score: parseInt(document.getElementById("f-credit").value),
    employment_type: document.getElementById("f-employment").value,
    existing_emis: parseFloat(document.getElementById("f-emis").value || 0),
    loan_amount: parseFloat(document.getElementById("f-loan").value),
    property_owned: document.getElementById("f-property").value === "true",
  };

  try {
    const res = await fetch("/recommend", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });
    const json = await res.json();
    if (json.status === "success") {
      state.lastResult = json.data;
      renderResults(json.data);
    } else {
      alert("Error: " + (json.message || "Recommendation failed."));
    }
  } catch (err) {
    alert("Network error. Is the Flask server running?");
    console.error(err);
  } finally {
    btn.disabled = false;
    btnText.classList.remove("hidden");
    spinner.classList.add("hidden");
  }
}

// ─── Render Results ─────────────────────────────────────────────────────────
function renderResults(data) {
  const area = document.getElementById("resultsArea");
  area.style.display = "block";
  area.scrollIntoView({ behavior: "smooth", block: "start" });

  // Decision banner
  const dec = data.final_decision;
  const banner = document.getElementById("decisionBanner");
  banner.className = "decision-banner " + dec.toLowerCase();
  const icons = { Approved: "&#10004;", Conditional: "&#9888;", Rejected: "&#10008;" };
  const subs = {
    Approved: "Your loan has been approved by multiple banks!",
    Conditional: "Conditional approval available with some requirements.",
    Rejected: "Unfortunately no banks can fully approve this request.",
  };
  document.getElementById("decisionIcon").innerHTML = icons[dec] || "";
  document.getElementById("decisionText").textContent = "Decision: " + dec;
  document.getElementById("decisionSub").textContent = subs[dec] || "";

  // Best bank card
  const bestCard = document.getElementById("bestBankCard");
  if (data.best_bank && data.recommended_banks.length > 0) {
    bestCard.style.display = "flex";
    const top = data.recommended_banks[0];
    document.getElementById("bestBankName").textContent = data.best_bank;
    document.getElementById("bestProb").textContent = (top.approval_probability * 100).toFixed(0) + "%";
    document.getElementById("bestRate").textContent = top.interest_rate;
    document.getElementById("bestLoan").textContent = fmt(top.max_loan);
    document.getElementById("bestDays").textContent = top.processing_days + " days";
  } else {
    bestCard.style.display = "none";
  }

  // Comparison table
  renderComparisonTable(data);

  // Conditional offer
  const cond = data.conditional_offer;
  const condCard = document.getElementById("conditionalCard");
  if (cond && cond.available) {
    condCard.classList.remove("hidden");
    document.getElementById("condBank").textContent = cond.bank;
    document.getElementById("condMaxLoan").textContent = fmt(cond.max_conditional_loan || 0);
    const list = document.getElementById("condList");
    list.innerHTML = "";
    (cond.conditions || [cond.condition]).forEach(c => {
      const li = document.createElement("li");
      li.textContent = c;
      list.appendChild(li);
    });
  } else {
    condCard.classList.add("hidden");
  }

  // Feature importance
  renderFeatureChips(data.top_features || []);

  // Reset chatbot
  document.getElementById("chatMessages").innerHTML =
    '<div class="chat-bubble bot">Results are in! Ask me anything about your recommendations.</div>';
}

function renderComparisonTable(data) {
  const tbody = document.getElementById("tableBody");
  tbody.innerHTML = "";
  const recommended = data.recommended_banks || [];
  const all = data.all_banks || [];
  const recNames = new Set(recommended.map(b => b.bank));
  const sorted = [
    ...recommended.map((b, i) => ({ ...b, rank: i + 1 })),
    ...all.filter(b => !recNames.has(b.bank)).map(b => ({ ...b, rank: "-" }))
  ];

  sorted.forEach(b => {
    const prob = b.approval_probability || 0;
    const probPct = (prob * 100).toFixed(0);
    const probClass = prob >= 0.7 ? "high" : prob >= 0.4 ? "med" : "low";
    const tr = document.createElement("tr");
    tr.innerHTML = `
      <td>${b.rank !== "-" ? `<span class="badge badge-rank">#${b.rank}</span>` : '<span style="color:var(--text-500)">-</span>'}</td>
      <td><strong>${b.bank}</strong></td>
      <td>${b.eligible ? '<span class="badge badge-eligible">Eligible</span>' : '<span class="badge badge-ineligible">Ineligible</span>'}</td>
      <td><span>${probPct}%</span> <div class="prob-bar-wrap"><div class="prob-bar-fill ${probClass}" style="width:${probPct}%"></div></div></td>
      <td>${b.interest_rate || "-"}</td>
      <td>${b.max_loan ? fmt(b.max_loan) : "-"}</td>
      <td>${b.collateral_required ? '<span class="badge badge-collateral">Required</span>' : '<span class="badge badge-no-collateral">None</span>'}</td>
      <td>${b.processing_days ? b.processing_days + "d" : "-"}</td>
      <td style="font-size:0.78rem;color:var(--text-300);max-width:180px;">${b.reason || "-"}</td>
    `;
    tbody.appendChild(tr);
  });
}

function renderFeatureChips(features) {
  const grid = document.getElementById("featuresGrid");
  grid.innerHTML = "";
  if (!features.length) return;
  const maxImp = Math.max(...features.map(f => f.importance));
  features.forEach(f => {
    const pct = ((f.importance / maxImp) * 100).toFixed(0);
    const div = document.createElement("div");
    div.className = "feature-chip";
    div.innerHTML = `
      <div class="feature-name">${f.feature.replace(/_/g, " ")}</div>
      <div class="feature-value">${(f.importance * 100).toFixed(1)}%</div>
      <div class="feature-bar-wrap"><div class="feature-bar-fill" style="width:${pct}%"></div></div>
    `;
    grid.appendChild(div);
  });
}

// ─── Chatbot ────────────────────────────────────────────────────────────────
async function sendChat(question) {
  if (!question?.trim()) return;
  const msgs = document.getElementById("chatMessages");
  const input = document.getElementById("chatInput");

  // User bubble
  const userBubble = document.createElement("div");
  userBubble.className = "chat-bubble user";
  userBubble.textContent = question;
  msgs.appendChild(userBubble);
  input.value = "";
  msgs.scrollTop = msgs.scrollHeight;

  try {
    const res = await fetch("/api/chatbot", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ question, context: state.lastResult || {} }),
    });
    const json = await res.json();
    const answer = json.status === "success" ? json.data.answer : "Sorry, I encountered an error.";
    const botBubble = document.createElement("div");
    botBubble.className = "chat-bubble bot";
    botBubble.textContent = answer;
    msgs.appendChild(botBubble);
  } catch {
    const errBubble = document.createElement("div");
    errBubble.className = "chat-bubble bot";
    errBubble.textContent = "Network error. Please check your connection.";
    msgs.appendChild(errBubble);
  }
  msgs.scrollTop = msgs.scrollHeight;
}

document.addEventListener("DOMContentLoaded", () => {
  document.getElementById("chatSendBtn")?.addEventListener("click", () => sendChat(document.getElementById("chatInput").value));
  document.getElementById("chatInput")?.addEventListener("keydown", e => { if (e.key === "Enter") sendChat(e.target.value); });
  document.querySelectorAll(".quick-btn").forEach(btn => btn.addEventListener("click", () => sendChat(btn.dataset.q)));
});

// ─── Reset ──────────────────────────────────────────────────────────────────
function resetForm() {
  document.getElementById("loan-form").reset();
  document.getElementById("resultsArea").style.display = "none";
  window.scrollTo({ top: 0, behavior: "smooth" });
}

// ─── Utilities ──────────────────────────────────────────────────────────────
function fmt(n) {
  if (n >= 10000000) return "\u20B9" + (n / 10000000).toFixed(2) + " Cr";
  if (n >= 100000)   return "\u20B9" + (n / 100000).toFixed(2) + " L";
  return "\u20B9" + Number(n).toLocaleString("en-IN");
}

function setText(id, val) {
  const el = document.getElementById(id);
  if (el) el.textContent = val;
}

function animateText(id, val) {
  const el = document.getElementById(id);
  if (!el) return;
  el.style.opacity = 0; el.textContent = val;
  el.style.transition = "opacity 0.5s";
  setTimeout(() => { el.style.opacity = 1; }, 100);
}

function setBarWidth(id, pct) {
  const el = document.getElementById(id);
  if (el) el.style.width = pct + "%";
}
