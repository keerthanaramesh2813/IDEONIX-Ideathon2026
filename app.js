let currentType = "message";

function showPage(id, btn) {
  document.querySelectorAll(".page").forEach(p => p.classList.add("hidden"));
  document.getElementById(id).classList.remove("hidden");
  document.getElementById("title").textContent =
    id === "student" ? "Student Safety" : id === "analyze" ? "Analyze Content" : "Admin Dashboard";
  document.querySelectorAll(".nav").forEach(n => n.classList.remove("active"));
  if (btn) btn.classList.add("active");
  if (id === "admin") loadDashboard();
  updateCounts();
}

function setType(type, el) {
  currentType = type;
  document.querySelectorAll(".tab").forEach(t => t.classList.remove("active"));
  el.classList.add("active");
  document.getElementById("content").placeholder =
    type === "url" ? "https://example.com/login/verify" :
    "Example: Your school account will be deleted. Send me your OTP immediately...";
}

async function analyze() {
  const content = document.getElementById("content").value.trim();
  if (!content) return alert("Please enter a message or URL.");
  const resultBox = document.getElementById("result");
  resultBox.classList.remove("hidden");
  resultBox.innerHTML = "<p>🔄 Analyzing content...</p>";

  const res = await fetch("/api/analyze", {
    method:"POST", headers:{"Content-Type":"application/json"},
    body:JSON.stringify({type:currentType,content})
  });
  const data = await res.json();
  if (!res.ok) { resultBox.innerHTML = `<p>${data.error}</p>`; return; }

  const cls = data.severity.toLowerCase();
  resultBox.innerHTML = `
    <div class="result-head">
      <div><span class="eyebrow">SAFETY ANALYSIS</span><h2>${escapeHtml(data.category)}</h2></div>
      <span class="severity ${cls}">${data.severity}</span>
    </div>
    <div class="risk">${data.riskScore}<small style="font-size:15px;color:#7b8798"> / 100 risk</small></div>
    <h3>Why this was flagged</h3>
    ${data.reasons.map(r=>`<div class="reason">• ${escapeHtml(r)}</div>`).join("")}
    <div class="recommend"><b>Recommendation</b><br>${escapeHtml(data.recommendation)}</div>
    <p class="muted">Incident ID: ${data.incidentId}</p>`;
  updateCounts();
}

async function loadDashboard() {
  const [d, r] = await Promise.all([fetch("/api/dashboard"), fetch("/api/incidents")]);
  const data = await d.json(), incidents = await r.json();
  document.getElementById("students").textContent = data.students.toLocaleString();
  document.getElementById("incidents").textContent = data.incidents;
  document.getElementById("critical").textContent = data.critical;
  document.getElementById("resolved").textContent = data.resolved;
  const rows = document.getElementById("incidentRows");
  rows.innerHTML = incidents.length ? incidents.map(i => `
    <tr>
      <td>${i.incidentId}</td><td>${i.type}</td><td>${escapeHtml(i.category)}</td>
      <td><span class="severity ${i.severity.toLowerCase()}">${i.riskScore}</span></td>
      <td class="status">${i.status}</td>
      <td>${i.status === "Open" ? `<button class="resolve" onclick="resolveIncident('${i.incidentId}')">Resolve</button>` : "✓"}</td>
    </tr>`).join("") :
    `<tr><td colspan="6" class="empty">No incidents yet. Analyze a message first.</td></tr>`;
}

async function resolveIncident(id) {
  await fetch(`/api/incidents/${id}/resolve`, {method:"POST"});
  loadDashboard();
}

async function updateCounts() {
  const r = await fetch("/api/dashboard"), d = await r.json();
  document.getElementById("scanCount").textContent = d.incidents;
  document.getElementById("warningCount").textContent = d.high + d.critical;
}

function escapeHtml(s) {
  return s.replace(/[&<>"']/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#039;'}[c]));
}
updateCounts();
