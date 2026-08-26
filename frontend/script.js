const API_BASE = "http://127.0.0.1:8000";

const manualMode = document.getElementById("manualMode");
const datasetMode = document.getElementById("datasetMode");
const manualForm = document.getElementById("manualForm");
const datasetForm = document.getElementById("datasetForm");
const analyzeBtn = document.getElementById("analyzeBtn");
const errorBox = document.getElementById("error");

let currentResults = [];

manualMode.addEventListener("click", () => {
  manualMode.classList.add("active");
  datasetMode.classList.remove("active");
  manualForm.classList.remove("hidden");
  datasetForm.classList.add("hidden");
});

datasetMode.addEventListener("click", () => {
  datasetMode.classList.add("active");
  manualMode.classList.remove("active");
  datasetForm.classList.remove("hidden");
  manualForm.classList.add("hidden");
});

function numberValue(id) {
  return Number(document.getElementById(id).value);
}

function getTransaction() {
  return {
    payment_method: document.getElementById("payment_method").value,
    gateway_status: document.getElementById("gateway_status").value,
    issuer_status: document.getElementById("issuer_status").value,
    amount: numberValue("amount"),
    card_age_days: numberValue("card_age_days"),
    card_expiry_days: numberValue("card_expiry_days"),
    retry_count: numberValue("retry_count"),
    customer_tenure_days: numberValue("customer_tenure_days"),
    customer_past_success_rate: numberValue("customer_past_success_rate"),
    gateway_response_time_ms: numberValue("gateway_response_time_ms"),
    issuer_response_time_ms: numberValue("issuer_response_time_ms"),
    risk_score: numberValue("risk_score"),
    available_balance_ratio: numberValue("available_balance_ratio"),
    transaction_limit: numberValue("transaction_limit"),
    otp_attempts: numberValue("otp_attempts"),
    cvv_match: numberValue("cvv_match"),
  };
}

async function analyze() {
  errorBox.textContent = "";
  analyzeBtn.disabled = true;
  analyzeBtn.textContent = "Analyzing...";

  try {
    let response;

    if (!manualForm.classList.contains("hidden")) {
      response = await fetch(`${API_BASE}/predict`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(getTransaction()),
      });
    } else {
      response = await fetch(
        `${API_BASE}/batch?n_rows=${numberValue("n_rows")}`,
        {
          method: "POST",
        },
      );
    }

    if (!response.ok) {
      throw new Error(await response.text());
    }

    const data = await response.json();

    if (Array.isArray(data.results)) {
      currentResults = data.results;
      renderResults(currentResults, data.summary);
    } else {
      currentResults = [data];
      renderResults(currentResults);
    }
  } catch (error) {
    errorBox.textContent = "Could not connect to the backend: " + error.message;
  } finally {
    analyzeBtn.disabled = false;
    analyzeBtn.textContent = "Analyze";
  }
}

function renderResults(results, summary = null) {
  document.getElementById("summary").classList.remove("hidden");
  document.getElementById("resultsCard").classList.remove("hidden");

  // Batch dataset result
  if (summary) {
    document.getElementById("processed").textContent = results.length;

    document.getElementById("totalAmount").textContent =
      `₹${summary.total_amount.toLocaleString("en-IN", {
        maximumFractionDigits: 2,
      })}`;

    document.getElementById("recoveredAmount").textContent =
      `₹${summary.recovered_amount.toLocaleString("en-IN", {
        maximumFractionDigits: 2,
      })}`;

    document.getElementById("amountAtRisk").textContent =
      `₹${summary.amount_at_risk.toLocaleString("en-IN", {
        maximumFractionDigits: 2,
      })}`;

    document.getElementById("review").textContent = summary.human_review;

    document.getElementById("rate").textContent =
      `${summary.recovery_rate.toFixed(1)}%`;
  }

  const body = document.getElementById("resultsBody");
  body.innerHTML = "";

  results.forEach((result, index) => {
    const row = document.createElement("tr");

    row.innerHTML = `
      <td>${result.transaction_id || `Transaction ${index + 1}`}</td>

      <td>
        ${result.predicted_root_cause || result.root_cause || "-"}
      </td>

      <td>
        ${((result.confidence || 0) * 100).toFixed(2)}%
      </td>

      <td>
        ${result.recovered ? "Recovered" : "Not recovered"}
      </td>

      <td>
        ${result.recovery_attempts ?? "-"}
      </td>

      <td>
        ${result.recommended_action || "-"}
      </td>
    `;

    row.addEventListener("click", () => showDetails(result));
    body.appendChild(row);
  });
}

function showDetails(result) {
  const card = document.getElementById("detailCard");
  const details = document.getElementById("details");

  card.classList.remove("hidden");

  details.innerHTML = `
        <p><strong>Root Cause:</strong>
            ${result.predicted_root_cause || result.root_cause || "-"}</p>

        <p><strong>Confidence:</strong>
            ${((result.confidence || 0) * 100).toFixed(2)}%</p>

        <p><strong>Reason:</strong>
            ${result.reason || "-"}</p>

        <p><strong>Recommended Action:</strong>
            ${result.recommended_action || "-"}</p>

        <p><strong>Recovered:</strong>
            ${result.recovered ? "Yes" : "No"}</p>

        <p><strong>Recovery Attempts:</strong>
            ${result.recovery_attempts ?? "-"}</p>
    `;

  card.scrollIntoView({ behavior: "smooth" });
}

analyzeBtn.addEventListener("click", analyze);
