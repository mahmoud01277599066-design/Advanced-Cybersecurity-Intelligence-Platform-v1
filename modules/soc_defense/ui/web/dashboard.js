const refreshNowBtn = document.getElementById("refreshNowBtn");
const sendAlertBtn = document.getElementById("sendAlertBtn");
const sendResult = document.getElementById("sendResult");
const alertsTableBody = document.getElementById("alertsTableBody");
const alertDetails = document.getElementById("alertDetails");
const lastRefresh = document.getElementById("lastRefresh");
const alertJsonInput = document.getElementById("alertJsonInput");
const approveMitigateBtn = document.getElementById("approveMitigateBtn");
const investigateBtn = document.getElementById("investigateBtn");
const dismissAlertBtn = document.getElementById("dismissAlertBtn");
const hitlResult = document.getElementById("hitlResult");

const metricTotal = document.getElementById("metricTotal");
const metricCritical = document.getElementById("metricCritical");
const metricHigh = document.getElementById("metricHigh");
const metricLatest = document.getElementById("metricLatest");
const metricSuccess = document.getElementById("metricSuccess");

const typeBars = document.getElementById("typeBars");
const routerBars = document.getElementById("routerBars");
const statusBars = document.getElementById("statusBars");

let cachedAlerts = [];
let selectedAlertId = null;

const defaultPayload = {
  alert_id: "soc-alert-004",
  alert_type: "code_vulnerability",
  severity: 3.2,
  title: "Information Exposure via Verbose Error Message",
  description:
    "Application returns detailed error messages exposing internal system information",
  source_module: "soc",
  affected_target: "192.168.56.104",
  code_snippet: "return str(exception)",
  file_path: "utils/error_handler.py",
  network_details: null,
  raw_data: {
    example_error: "DatabaseError: connection failed at db.internal.local:5432",
    exposed_details: ["internal hostname", "database type", "stack trace fragment"],
  },
  timestamp: "2026-04-17T13:15:00Z",
};

alertJsonInput.value = JSON.stringify(defaultPayload, null, 2);

function severityClass(score) {
  const val = Number(score) || 0;
  if (val >= 9) return "CRITICAL";
  if (val >= 7) return "HIGH";
  if (val >= 4) return "MEDIUM";
  if (val > 0) return "LOW";
  return "NONE";
}

function renderBars(container, dataObj) {
  const entries = Object.entries(dataObj || {});
  const total = entries.reduce((acc, item) => acc + Number(item[1] || 0), 0) || 1;

  if (entries.length === 0) {
    container.innerHTML = '<span class="pill">No data</span>';
    return;
  }

  container.innerHTML = entries
    .map(([label, count]) => {
      const value = Number(count || 0);
      const width = Math.max(3, Math.round((value / total) * 100));
      return `
        <div class="bar-item">
          <div class="bar-label"><span>${label}</span><strong>${value}</strong></div>
          <div class="bar-track"><div class="bar-fill" style="width:${width}%"></div></div>
        </div>
      `;
    })
    .join("");
}

function renderSelectedAlert(alert) {
  if (!alert) {
    alertDetails.textContent = "Select an alert from the table.";
    hitlResult.textContent = "Select alert";
    return;
  }

  alertDetails.textContent = JSON.stringify(alert, null, 2);
  hitlResult.textContent = `Current status: ${alert.status || "unknown"}`;
}

function renderAlertsTable(alerts) {
  if (!alerts.length) {
    alertsTableBody.innerHTML = '<tr><td colspan="7">No SOC alerts yet.</td></tr>';
    renderSelectedAlert(null);
    return;
  }

  alertsTableBody.innerHTML = alerts
    .map(
      (alert) => `
      <tr data-alert-id="${alert.alert_id}">
        <td>${alert.alert_id}</td>
        <td>${alert.alert_type || "-"}</td>
        <td><span class="sev-pill ${alert.risk_level || severityClass(alert.severity)}">${Number(alert.severity || 0).toFixed(1)}</span></td>
        <td>${alert.router_name || "-"}</td>
        <td><span class="status-pill ${String(alert.status || "unknown").toLowerCase()}">${alert.status || "unknown"}</span></td>
        <td>${alert.affected_target || "-"}</td>
        <td>${alert.timestamp || "-"}</td>
      </tr>
    `
    )
    .join("");

  alertsTableBody.querySelectorAll("tr[data-alert-id]").forEach((row) => {
    row.addEventListener("click", () => {
      selectedAlertId = row.dataset.alertId;
      const selected = cachedAlerts.find((a) => a.alert_id === selectedAlertId);
      renderSelectedAlert(selected);
    });
  });

  if (!selectedAlertId && alerts[0]) {
    selectedAlertId = alerts[0].alert_id;
  }

  const selected = cachedAlerts.find((a) => a.alert_id === selectedAlertId) || alerts[0];
  if (selected) {
    renderSelectedAlert(selected);
  }
}

async function loadSummary() {
  const res = await fetch("/api/v1/soc/dashboard/summary");
  if (!res.ok) throw new Error("Failed loading summary");

  const data = await res.json();
  const summary = data.summary || {};

  metricTotal.textContent = summary.total_alerts ?? 0;
  metricCritical.textContent = summary.critical_alerts ?? 0;
  metricHigh.textContent = summary.high_alerts ?? 0;
  metricLatest.textContent = summary.latest_alert_id || "-";
  metricSuccess.textContent = summary.successful_outputs ?? 0;

  renderBars(typeBars, data.type_distribution || {});
  renderBars(routerBars, data.router_distribution || {});
  renderBars(statusBars, data.status_distribution || {});
}

async function loadAlerts() {
  const res = await fetch("/api/v1/soc/alerts?limit=100");
  if (!res.ok) throw new Error("Failed loading alerts");

  const data = await res.json();
  cachedAlerts = Array.isArray(data.items) ? data.items : [];
  renderAlertsTable(cachedAlerts);
}

async function refreshDashboard() {
  try {
    await Promise.all([loadSummary(), loadAlerts()]);
    lastRefresh.textContent = `Last refresh: ${new Date().toLocaleTimeString()}`;
  } catch (err) {
    lastRefresh.textContent = `Refresh error: ${err.message}`;
  }
}

async function sendAlert() {
  let payload;
  sendResult.textContent = "Sending...";

  try {
    payload = JSON.parse(alertJsonInput.value);
  } catch (err) {
    sendResult.textContent = "Invalid JSON";
    return;
  }

  try {
    const res = await fetch("/api/v1/soc/ingest", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });

    const body = await res.json();
    if (!res.ok) {
      throw new Error(body.detail || "Failed to send");
    }

    sendResult.textContent = `Sent: ${body.alert_id}`;
    selectedAlertId = body.alert_id;
    await refreshDashboard();
  } catch (err) {
    sendResult.textContent = `Error: ${err.message}`;
  }
}

async function updateHitlStatus(status, label) {
  if (!selectedAlertId) {
    hitlResult.textContent = "Select alert first";
    return;
  }

  hitlResult.textContent = "Updating...";

  try {
    const res = await fetch(`/api/v1/soc/alerts/${encodeURIComponent(selectedAlertId)}/status`, {
      method: "PATCH",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ status, decision: label }),
    });

    const body = await res.json();
    if (!res.ok) {
      throw new Error(body.detail || "Failed to update HITL status");
    }

    const index = cachedAlerts.findIndex((alert) => alert.alert_id === selectedAlertId);
    if (index >= 0) {
      cachedAlerts[index] = body;
    }

    renderAlertsTable(cachedAlerts);
    renderSelectedAlert(body);
    hitlResult.textContent = `Decision saved: ${label}`;
    await loadSummary();
  } catch (err) {
    hitlResult.textContent = `Error: ${err.message}`;
  }
}

refreshNowBtn.addEventListener("click", refreshDashboard);
sendAlertBtn.addEventListener("click", sendAlert);
approveMitigateBtn.addEventListener("click", () => updateHitlStatus("approved_mitigated", "Approve & Mitigate"));
investigateBtn.addEventListener("click", () => updateHitlStatus("investigating", "Investigate"));
dismissAlertBtn.addEventListener("click", () => updateHitlStatus("dismissed", "Dismiss Alert"));

refreshDashboard();
setInterval(refreshDashboard, 5000);
