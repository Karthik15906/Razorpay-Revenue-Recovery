const API_BASE = "http://127.0.0.1:8000";

const manualMode = document.getElementById("manualMode");
const datasetMode = document.getElementById("datasetMode");
const manualForm = document.getElementById("manualForm");
const datasetForm = document.getElementById("datasetForm");
const analyzeBtn = document.getElementById("analyzeBtn");
const errorBox = document.getElementById("error");

let currentResults = [];

/* =========================
   MODE SWITCHING
========================= */

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

/* =========================
   HELPERS
========================= */

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

/* =========================
   ANALYZE
========================= */

async function analyze() {
  errorBox.textContent = "";

  analyzeBtn.disabled = true;
  analyzeBtn.textContent = "Analyzing...";

  try {
    let response;

    /* Manual transaction */

    if (!manualForm.classList.contains("hidden")) {
      response = await fetch(`${API_BASE}/predict`, {
        method: "POST",

        headers: {
          "Content-Type": "application/json",
        },

        body: JSON.stringify(getTransaction()),
      });
    } else {
      /* Generated dataset */
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

      const amount = Number(data.transaction?.amount || 0);
      const recovered = Boolean(data.recovered);

      const manualSummary = {
        total_amount: amount,

        recovered_amount: recovered ? amount : 0,

        amount_at_risk: recovered ? 0 : amount,

        human_review: data.recovery_decision === "human_review" ? 1 : 0,

        recovery_rate: recovered ? 100 : 0,
      };

      renderResults(currentResults, manualSummary);
    }
  } catch (error) {
    errorBox.textContent = "Could not connect to the backend: " + error.message;
  } finally {
    analyzeBtn.disabled = false;
    analyzeBtn.textContent = "Analyze";
  }
}

/* =========================
   FORMATTERS
========================= */

function formatProbability(value) {
  if (value === undefined || value === null) {
    return "-";
  }

  return `${(value * 100).toFixed(2)}%`;
}

function formatAmount(value) {
  if (value === undefined || value === null) {
    return "₹0";
  }

  return `₹${Number(value).toLocaleString("en-IN", {
    maximumFractionDigits: 2,
  })}`;
}

function decisionClass(decision) {
  if (decision === "recover") {
    return "decision-recover";
  }

  if (decision === "human_review") {
    return "decision-review";
  }

  if (decision === "do_not_recover") {
    return "decision-stop";
  }

  return "";
}

function recoveryStatus(result) {
  if (result.recovered) {
    return "Recovered";
  }

  if (result.recovery_decision === "do_not_recover") {
    return "Not attempted";
  }

  if (result.recovery_decision === "human_review") {
    return "Human review";
  }

  return "Not recovered";
}

/* =========================
   RENDER RESULTS
========================= */

function renderResults(results, summary = null) {
  document.getElementById("summary").classList.remove("hidden");
  document.getElementById("resultsCard").classList.remove("hidden");

  // =========================
  // BATCH RESULT
  // =========================
  if (summary) {
    document.getElementById("processed").textContent =
      summary.processed ?? results.length;

    document.getElementById("totalAmount").textContent = `₹${Number(
      summary.total_amount || 0,
    ).toLocaleString("en-IN", {
      maximumFractionDigits: 2,
    })}`;

    document.getElementById("recoveredAmount").textContent = `₹${Number(
      summary.recovered_amount || 0,
    ).toLocaleString("en-IN", {
      maximumFractionDigits: 2,
    })}`;

    document.getElementById("amountAtRisk").textContent = `₹${Number(
      summary.amount_at_risk || 0,
    ).toLocaleString("en-IN", {
      maximumFractionDigits: 2,
    })}`;

    document.getElementById("review").textContent = summary.human_review ?? 0;

    document.getElementById("rate").textContent =
      `${Number(summary.recovery_rate || 0).toFixed(1)}%`;
  }

  // =========================
  // MANUAL RESULT
  // =========================
  else if (results.length === 1) {
    const result = results[0];

    const amount = Number(document.getElementById("amount").value);

    const recovered = Boolean(result.recovered);

    const isHumanReview =
      result.recovery_decision === "human_review" ||
      result.recommended_action?.toLowerCase().includes("human review");

    document.getElementById("processed").textContent = "1";

    document.getElementById("totalAmount").textContent =
      `₹${amount.toLocaleString("en-IN", {
        maximumFractionDigits: 2,
      })}`;

    document.getElementById("recoveredAmount").textContent = recovered
      ? `₹${amount.toLocaleString("en-IN", {
          maximumFractionDigits: 2,
        })}`
      : "₹0";

    document.getElementById("amountAtRisk").textContent = recovered
      ? "₹0"
      : `₹${amount.toLocaleString("en-IN", {
          maximumFractionDigits: 2,
        })}`;

    document.getElementById("review").textContent = isHumanReview ? "1" : "0";

    document.getElementById("rate").textContent = recovered ? "100%" : "0%";
  }

  // =========================
  // TABLE
  // =========================

  const body = document.getElementById("resultsBody");

  body.innerHTML = "";

  results.forEach((result, index) => {
    const row = document.createElement("tr");

    const rootCause = result.predicted_root_cause || result.root_cause || "-";

    const confidence = Number(result.confidence || 0) * 100;

    const recoveryProbability = Number(result.recovery_probability || 0) * 100;

    const decision = result.recovery_decision || "-";

    let recoveredText = "Not recovered";

    if (result.recovered === true || result.recovered === 1) {
      recoveredText = "Recovered";
    } else if (decision === "human_review") {
      recoveredText = "Human review";
    }

    row.innerHTML = `
      <td>
        ${result.transaction_id || "MANUAL"}
      </td>

      <td>
        ${rootCause}
      </td>

      <td>
        ${confidence.toFixed(2)}%
      </td>

      <td>
        ${
          result.recovery_probability !== undefined
            ? recoveryProbability.toFixed(2) + "%"
            : "-"
        }
      </td>

      <td>
        ${decision.replaceAll("_", " ").toUpperCase()}
      </td>

      <td>
        ${recoveredText}
      </td>

      <td>
        ${result.recovery_attempts ?? 0}
      </td>
    `;

    row.addEventListener("click", () => {
      showDetails(result);
    });

    body.appendChild(row);
  });
}

/* =========================
   DETAILS
========================= */

function showDetails(result) {
  const card = document.getElementById("detailCard");
  const details = document.getElementById("details");

  card.classList.remove("hidden");

  const recoveryProbability =
    result.recovery_probability !== undefined
      ? `${(Number(result.recovery_probability) * 100).toFixed(2)}%`
      : "-";

  const decision = result.recovery_decision
    ? result.recovery_decision.replaceAll("_", " ").toUpperCase()
    : "-";

  details.innerHTML = `
    <p>
      <strong>Root Cause:</strong>
      ${result.predicted_root_cause || result.root_cause || "-"}
    </p>

    <p>
      <strong>Confidence:</strong>
      ${((Number(result.confidence) || 0) * 100).toFixed(2)}%
    </p>

    <p>
      <strong>Reason:</strong>
      ${result.reason || "-"}
    </p>

    <p>
      <strong>Recovery Probability:</strong>
      ${recoveryProbability}
    </p>

    <p>
      <strong>Recovery Decision:</strong>
      ${decision}
    </p>

    <p>
      <strong>Decision Reason:</strong>
      ${result.decision_reason || "-"}
    </p>

    <p>
      <strong>Recommended Action:</strong>
      ${result.recommended_action || "-"}
    </p>

    <p>
      <strong>Recovered:</strong>
      ${result.recovered === true || result.recovered === 1 ? "Yes" : "No"}
    </p>

    <p>
      <strong>Recovery Attempts:</strong>
      ${result.recovery_attempts ?? 0}
    </p>
  `;

  card.scrollIntoView({
    behavior: "smooth",
  });
}
/* =========================
   BUTTON
========================= */

analyzeBtn.addEventListener("click", analyze);
