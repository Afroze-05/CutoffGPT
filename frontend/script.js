/**
 * CollegePath AI - Frontend JavaScript
 * =====================================
 * Handles all UI interactions, API calls, map rendering, and chatbot.
 * Written in plain Vanilla JS - no frameworks needed!
 *
 * KEY FIX LOG (v2):
 *  - Upload handlers now show inline status messages for EVERY outcome
 *    (selecting a file, uploading, success, network error, server error)
 *  - showUploadStatus() helper centralises all status rendering
 *  - response.ok checked before .json() to catch HTTP 4xx/5xx properly
 *  - Network errors (backend offline) caught and shown clearly
 *  - File-size validation before attempting upload
 *  - Upload zone visual feedback restored after error
 */

// ── Backend API URL ──────────────────────────────────────────────
// Change this if your backend runs on a different port
const API_BASE = "http://localhost:8000";

// ── Global State ────────────────────────────────────────────────
let mapInstance       = null;
let currentRecommendations = {};
let quizAnswers       = {};

// ─────────────────────────────────────────────────────────────────
// UTILITY FUNCTIONS
// ─────────────────────────────────────────────────────────────────

function scrollToSection(id) {
  document.getElementById(id)?.scrollIntoView({ behavior: "smooth" });
}

function showLoading(message = "Processing...") {
  document.getElementById("loading-overlay").style.display = "flex";
  document.getElementById("loading-text").textContent = message;
}
function hideLoading() {
  document.getElementById("loading-overlay").style.display = "none";
}

/**
 * showUploadStatus(divId, type, html)
 * ------------------------------------
 * type = "info" | "success" | "error" | "warning"
 * Always makes the div visible and applies the right colour scheme.
 * This is the SINGLE place that controls upload result styling.
 */
function showUploadStatus(divId, type, html) {
  const div = document.getElementById(divId);
  if (!div) return;

  // Colour map per status type
  const styles = {
    info:    { bg: "rgba(56,189,248,0.08)",  border: "rgba(56,189,248,0.3)",  color: "#7dd3fc" },
    success: { bg: "rgba(52,211,153,0.08)",  border: "rgba(52,211,153,0.3)",  color: "#6ee7b7" },
    error:   { bg: "rgba(248,113,113,0.08)", border: "rgba(248,113,113,0.3)", color: "#fca5a5" },
    warning: { bg: "rgba(251,146,60,0.08)",  border: "rgba(251,146,60,0.3)",  color: "#fdba74" },
  };

  const s = styles[type] || styles.info;
  div.style.display       = "block";
  div.style.background    = s.bg;
  div.style.border        = `1px solid ${s.border}`;
  div.style.color         = s.color;
  div.style.padding       = "12px 16px";
  div.style.borderRadius  = "8px";
  div.style.marginTop     = "14px";
  div.style.fontSize      = "0.85rem";
  div.style.lineHeight    = "1.6";
  div.innerHTML = html;
}

/** Update the upload zone's visual appearance */
function setZoneState(zoneId, state, fileName) {
  const zone = document.getElementById(zoneId);
  if (!zone) return;
  const iconEl = zone.querySelector(".upload-zone-icon");
  const textEl = zone.querySelector(".upload-zone-text");
  const hintEl = zone.querySelector(".upload-zone-hint");

  if (state === "selected") {
    if (iconEl) iconEl.textContent = "📎";
    if (textEl) textEl.textContent = fileName;
    if (hintEl) hintEl.textContent = "Click Upload to proceed";
    zone.style.borderColor = "var(--accent)";
    zone.style.background  = "rgba(56,189,248,0.04)";
  } else if (state === "uploading") {
    if (iconEl) iconEl.textContent = "⏳";
    if (textEl) textEl.textContent = "Uploading…";
    zone.style.borderColor = "var(--accent)";
  } else if (state === "success") {
    if (iconEl) iconEl.textContent = "✅";
    if (textEl) textEl.textContent = fileName;
    if (hintEl) hintEl.textContent = "Upload successful";
    zone.style.borderColor = "var(--success, #34d399)";
    zone.style.background  = "rgba(52,211,153,0.04)";
  } else if (state === "error") {
    if (iconEl) iconEl.textContent = "❌";
    if (textEl) textEl.textContent = "Upload failed";
    if (hintEl) hintEl.textContent = "Try again";
    zone.style.borderColor = "rgba(248,113,113,0.5)";
    zone.style.background  = "rgba(248,113,113,0.04)";
  } else {
    // reset
    if (iconEl) iconEl.textContent = "⬆";
    if (textEl) textEl.textContent = "Drag & drop or click to upload";
    if (hintEl) hintEl.textContent = "JPG, PNG, or PDF";
    zone.style.borderColor = "";
    zone.style.background  = "";
  }
}

/** Safe JSON parse — returns null on failure */
async function safeJson(response) {
  try { return await response.json(); }
  catch { return null; }
}

/** Generic POST with JSON body */
async function apiPost(endpoint, data) {
  const response = await fetch(`${API_BASE}${endpoint}`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(data),
  });
  if (!response.ok) {
    const err = await safeJson(response);
    throw new Error(err?.detail || `Server error ${response.status}`);
  }
  return response.json();
}

/** Generic GET */
async function apiGet(endpoint) {
  const response = await fetch(`${API_BASE}${endpoint}`);
  if (!response.ok) throw new Error(`Server error ${response.status}`);
  return response.json();
}

function formatINR(amount) {
  if (amount >= 100000) return `₹${(amount / 100000).toFixed(1)}L`;
  if (amount >= 1000)   return `₹${(amount / 1000).toFixed(0)}K`;
  return `₹${amount}`;
}

// ─────────────────────────────────────────────────────────────────
// UPLOAD HANDLERS  ← FULLY REWRITTEN
// ─────────────────────────────────────────────────────────────────

/**
 * handleMarksheetUpload
 * ----------------------
 * Called when the student selects a marksheet file.
 * Steps:
 *   1. Validate file type & size
 *   2. Show "uploading" state immediately so user knows something is happening
 *   3. POST to /upload-marksheet
 *   4. On success → show extracted data + auto-fill form
 *   5. On ANY error → show a clear, readable error message
 */
async function handleMarksheetUpload(event) {
  const file = event.target.files[0];
  if (!file) return;

  const resultDivId = "marksheet-result";

  // ── Step 1: Client-side validation ──────────────────────────
  const allowedTypes = ["image/jpeg", "image/jpg", "image/png", "application/pdf"];
  if (!allowedTypes.includes(file.type)) {
    setZoneState("marksheet-zone", "error", file.name);
    showUploadStatus(resultDivId, "error",
      `❌ <strong>Wrong file type.</strong><br>
       Please upload a <strong>JPG, PNG, or PDF</strong> file.<br>
       You selected: <em>${file.type || "unknown type"}</em>`
    );
    return;
  }

  const maxSizeMB = 10;
  if (file.size > maxSizeMB * 1024 * 1024) {
    setZoneState("marksheet-zone", "error", file.name);
    showUploadStatus(resultDivId, "error",
      `❌ <strong>File too large.</strong><br>
       Maximum allowed size is ${maxSizeMB} MB.<br>
       Your file: ${(file.size / 1024 / 1024).toFixed(1)} MB`
    );
    return;
  }

  // ── Step 2: Show immediate feedback ─────────────────────────
  setZoneState("marksheet-zone", "uploading", file.name);
  showUploadStatus(resultDivId, "info",
    `⏳ <strong>Uploading "${file.name}"…</strong><br>
     Running OCR analysis on your marksheet. Please wait.`
  );

  showLoading("Analyzing marksheet with OCR…");

  try {
    // ── Step 3: Send file to backend ─────────────────────────
    const formData = new FormData();
    formData.append("file", file);

    let response;
    try {
      response = await fetch(`${API_BASE}/upload-marksheet`, {
        method: "POST",
        body: formData,
        // Do NOT set Content-Type manually — browser adds the multipart boundary
      });
    } catch (networkErr) {
      // fetch() itself threw → backend is likely offline
      throw new Error(
        "Cannot reach the backend server. " +
        "Make sure it is running: cd backend && uvicorn main:app --reload --port 8000"
      );
    }

    // ── Step 4: Handle server response ───────────────────────
    if (!response.ok) {
      const errBody = await safeJson(response);
      throw new Error(
        errBody?.detail ||
        `Server returned HTTP ${response.status} ${response.statusText}`
      );
    }

    const data = await response.json();
    const extracted = data.extracted_data || {};

    // ── Step 5: Show success ──────────────────────────────────
    setZoneState("marksheet-zone", "success", file.name);
    showUploadStatus(resultDivId, "success",
      `✅ <strong>Marksheet analysed successfully!</strong><br><br>
       👤 Name: <strong>${extracted.student_name || "Not detected"}</strong><br>
       📊 Percentage: <strong>${extracted.percentage != null ? extracted.percentage + "%" : "Not detected"}</strong><br>
       🏆 Rank: <strong>${extracted.rank || "Not found"}</strong><br>
       🏷️ Category: <strong>${extracted.category || "OPEN"}</strong>
       ${extracted.note
         ? `<br><br><em style="opacity:0.7;font-size:0.8em">ℹ️ ${extracted.note}</em>`
         : ""}
       <br><br><span style="opacity:0.7">Form below has been auto-filled ↓</span>`
    );

    // Auto-fill the preferences form
    if (extracted.student_name) document.getElementById("student-name").value  = extracted.student_name;
    if (extracted.percentage)   document.getElementById("student-pct").value   = extracted.percentage;
    if (extracted.rank)         document.getElementById("student-rank").value  = extracted.rank;
    if (extracted.category)     document.getElementById("student-category").value = extracted.category;

    setTimeout(() => scrollToSection("recommend-section"), 1200);

  } catch (error) {
    // ── Step 6: Show error clearly ────────────────────────────
    setZoneState("marksheet-zone", "error", file.name);
    showUploadStatus(resultDivId, "error",
      `❌ <strong>Upload failed</strong><br><br>
       ${error.message}<br><br>
       <strong>Troubleshooting:</strong><br>
       • Is the backend running on port 8000?<br>
       • Run: <code style="background:rgba(0,0,0,0.3);padding:2px 6px;border-radius:4px">uvicorn main:app --reload --port 8000</code><br>
       • Check browser Console (F12) for more details`
    );
  } finally {
    hideLoading();
  }
}

/**
 * handleCutoffUpload
 * -------------------
 * Admin uploads a cutoff PDF.
 * Same robust pattern as marksheet upload.
 */
async function handleCutoffUpload(event) {
  const file = event.target.files[0];
  if (!file) return;

  const resultDivId = "cutoff-result";

  // ── Validate ─────────────────────────────────────────────────
  if (file.type !== "application/pdf" && !file.name.endsWith(".pdf")) {
    setZoneState("cutoff-zone", "error", file.name);
    showUploadStatus(resultDivId, "error",
      `❌ <strong>Only PDF files are accepted.</strong><br>
       You selected: <em>${file.name}</em>`
    );
    return;
  }

  const maxSizeMB = 50;
  if (file.size > maxSizeMB * 1024 * 1024) {
    setZoneState("cutoff-zone", "error", file.name);
    showUploadStatus(resultDivId, "error",
      `❌ <strong>File too large.</strong> Max ${maxSizeMB} MB allowed.<br>
       Your file: ${(file.size / 1024 / 1024).toFixed(1)} MB`
    );
    return;
  }

  // ── Immediate feedback ────────────────────────────────────────
  setZoneState("cutoff-zone", "uploading", file.name);
  showUploadStatus(resultDivId, "info",
    `⏳ <strong>Uploading "${file.name}"…</strong><br>
     Extracting college and cutoff data from PDF. This may take a moment.`
  );

  showLoading("Extracting college data from PDF…");

  try {
    const formData = new FormData();
    formData.append("file", file);

    let response;
    try {
      response = await fetch(`${API_BASE}/upload-cutoff`, {
        method: "POST",
        body: formData,
      });
    } catch (networkErr) {
      throw new Error(
        "Cannot reach the backend server. " +
        "Make sure it is running: cd backend && uvicorn main:app --reload --port 8000"
      );
    }

    if (!response.ok) {
      const errBody = await safeJson(response);
      throw new Error(
        errBody?.detail ||
        `Server returned HTTP ${response.status} ${response.statusText}`
      );
    }

    const data = await response.json();

    setZoneState("cutoff-zone", "success", file.name);
    showUploadStatus(resultDivId, "success",
      `✅ <strong>PDF processed successfully!</strong><br><br>
       📄 File: <strong>${data.filename || file.name}</strong><br>
       🏫 College records extracted: <strong>${data.records ?? 0}</strong><br><br>
       <span style="opacity:0.7">Data is now stored in the database and available for recommendations.</span>`
    );

  } catch (error) {
    setZoneState("cutoff-zone", "error", file.name);
    showUploadStatus(resultDivId, "error",
      `❌ <strong>Upload failed</strong><br><br>
       ${error.message}<br><br>
       <strong>Troubleshooting:</strong><br>
       • Is the backend running on port 8000?<br>
       • Run: <code style="background:rgba(0,0,0,0.3);padding:2px 6px;border-radius:4px">uvicorn main:app --reload --port 8000</code><br>
       • Check browser Console (F12) for more details`
    );
  } finally {
    hideLoading();
  }
}

// ─────────────────────────────────────────────────────────────────
// RECOMMENDATION ENGINE
// ─────────────────────────────────────────────────────────────────

async function handleRecommendation(event) {
  event.preventDefault();

  const preferences = {
    student_name:       document.getElementById("student-name").value,
    percentage:         parseFloat(document.getElementById("student-pct").value),
    rank:               parseInt(document.getElementById("student-rank").value) || null,
    category:           document.getElementById("student-category").value,
    preferred_branch:   document.getElementById("student-branch").value,
    preferred_city:     document.getElementById("student-city").value,
    budget:             parseInt(document.getElementById("student-budget").value),
    hostel_needed:      document.getElementById("hostel-needed").checked,
    govt_preferred:     document.getElementById("govt-preferred").checked,
    placement_priority: document.getElementById("placement-priority").checked,
  };

  showLoading("Finding your perfect colleges…");

  try {
    const data = await apiPost("/recommend", preferences);
    currentRecommendations = data;

    const resultsDiv = document.getElementById("recommendation-results");
    resultsDiv.style.display = "block";

    document.getElementById("dream-count").textContent  = data.dream_colleges?.length  || 0;
    document.getElementById("target-count").textContent = data.target_colleges?.length || 0;
    document.getElementById("safe-count").textContent   = data.safe_colleges?.length   || 0;

    const summary = data.student_summary || {};
    document.getElementById("results-subtitle").textContent =
      `For ${summary.name || "you"} • ${summary.percentage}% • ${summary.category} • ${summary.branch}`;

    renderCollegeCards("dream-colleges",  data.dream_colleges  || []);
    renderCollegeCards("target-colleges", data.target_colleges || []);
    renderCollegeCards("safe-colleges",   data.safe_colleges   || []);

    showTab("dream");
    setTimeout(() => resultsDiv.scrollIntoView({ behavior: "smooth" }), 300);

    updateMapMarkers([
      ...(data.dream_colleges  || []),
      ...(data.target_colleges || []),
      ...(data.safe_colleges   || []),
    ]);

  } catch (error) {
    alert(`Recommendation error: ${error.message}\n\nMake sure the backend server is running on port 8000.`);
  } finally {
    hideLoading();
  }
}

function renderCollegeCards(containerId, colleges) {
  const container = document.getElementById(containerId);

  if (!colleges || colleges.length === 0) {
    container.innerHTML = `
      <div style="grid-column:1/-1;text-align:center;color:var(--text-muted);padding:40px">
        No colleges found in this category with your current filters.
      </div>`;
    return;
  }

  container.innerHTML = colleges.map((college, index) => `
    <div class="college-card" style="animation-delay:${index * 0.08}s"
         onclick="showCollegeOnMap(${college.latitude}, ${college.longitude}, '${college.name.replace(/'/g,"\\'")}')">
      <div class="card-header">
        <div>
          <div class="card-college-name">${college.name}</div>
          <div class="card-branch">${college.branch}</div>
        </div>
        <span class="probability-badge ${getProbClass(college.admission_probability)}">
          ${college.admission_probability}% chance
        </span>
      </div>
      <div class="card-stats">
        <div class="card-stat">
          <div class="card-stat-label">Cutoff</div>
          <div class="card-stat-value">${college.cutoff_percentile}%</div>
        </div>
        <div class="card-stat">
          <div class="card-stat-label">Fees/Year</div>
          <div class="card-stat-value">${formatINR(college.fees)}</div>
        </div>
        <div class="card-stat">
          <div class="card-stat-label">Placements</div>
          <div class="card-stat-value">${college.placements_avg} LPA</div>
        </div>
        <div class="card-stat">
          <div class="card-stat-label">NAAC</div>
          <div class="card-stat-value">${college.naac_grade}</div>
        </div>
      </div>
      <div class="card-tags">
        <span class="card-tag">${college.city}</span>
        <span class="card-tag">${college.type}</span>
        ${college.hostel_available ? '<span class="card-tag">Hostel ✓</span>' : ""}
        <span class="card-tag">${college.match_label}</span>
      </div>
      <div class="probability-bar">
        <div class="prob-label">
          <span>Admission Probability</span>
          <span>${college.admission_probability}%</span>
        </div>
        <div class="prob-track">
          <div class="prob-fill" style="width:${college.admission_probability}%"></div>
        </div>
      </div>
    </div>
  `).join("");
}

function getProbClass(prob) {
  if (prob >= 70) return "prob-high";
  if (prob >= 40) return "prob-medium";
  return "prob-low";
}

function showTab(tabName) {
  ["dream-colleges", "target-colleges", "safe-colleges"].forEach(id => {
    document.getElementById(id).style.display = "none";
  });
  document.querySelectorAll(".tab-btn").forEach(btn => btn.classList.remove("active"));

  document.getElementById(`${tabName}-colleges`).style.display = "grid";
  const idx = { dream: 0, target: 1, safe: 2 }[tabName];
  const btns = document.querySelectorAll(".tab-btn");
  if (btns[idx]) btns[idx].classList.add("active");
}

// ─────────────────────────────────────────────────────────────────
// COLLEGE COMPARISON
// ─────────────────────────────────────────────────────────────────

async function handleCompare() {
  const names = [
    document.getElementById("compare-input-1").value.trim(),
    document.getElementById("compare-input-2").value.trim(),
    document.getElementById("compare-input-3").value.trim(),
  ].filter(n => n.length > 0);

  if (names.length < 2) {
    alert("Please enter at least 2 college names to compare.");
    return;
  }

  showLoading("Fetching college data…");

  try {
    const data = await apiGet(`/compare?names=${encodeURIComponent(names.join(","))}`);
    renderCompareTable(data.colleges || []);
    document.getElementById("compare-results").style.display = "block";
  } catch (error) {
    alert(`Compare error: ${error.message}`);
  } finally {
    hideLoading();
  }
}

function renderCompareTable(colleges) {
  if (!colleges.length) {
    document.getElementById("compare-table").innerHTML =
      `<tr><td colspan="10" style="text-align:center;color:var(--text-muted);padding:40px">
        No colleges found. Try different names.
      </td></tr>`;
    return;
  }

  const rows = [
    { label: "College Name",  key: "name" },
    { label: "Branch",        key: "branch" },
    { label: "City",          key: "city" },
    { label: "Type",          key: "type" },
    { label: "Cutoff %ile",   key: "cutoff_percentile" },
    { label: "Annual Fees",   key: "fees",             format: formatINR },
    { label: "Avg Placement", key: "placements_avg",   format: v => `${v} LPA` },
    { label: "NAAC Grade",    key: "naac_grade" },
    { label: "Hostel",        key: "hostel_available", format: v => v ? "✅ Yes" : "❌ No" },
  ];

  let header = "<thead><tr><th>Metric</th>";
  colleges.forEach(c => { header += `<th>${c.name}</th>`; });
  header += "</tr></thead>";

  let body = "<tbody>";
  rows.forEach(row => {
    body += `<tr><td>${row.label}</td>`;
    colleges.forEach(college => {
      const val = college[row.key];
      body += `<td>${row.format ? row.format(val) : (val ?? "N/A")}</td>`;
    });
    body += "</tr>";
  });
  body += "</tbody>";

  document.getElementById("compare-table").innerHTML = header + body;
}

// ─────────────────────────────────────────────────────────────────
// MAP (Leaflet.js)
// ─────────────────────────────────────────────────────────────────

const SAMPLE_LOCATIONS = [
  { name: "COEP Pune",       lat: 18.5314, lng: 73.8446, type: "government", branch: "CS, Mech, Civil" },
  { name: "PCCOE Pune",      lat: 18.6526, lng: 73.7763, type: "private",    branch: "CS, AI, IT" },
  { name: "VIT Pune",        lat: 18.4673, lng: 73.8671, type: "private",    branch: "CS, ENTC, Mech" },
  { name: "Symbiosis IT",    lat: 18.5089, lng: 73.9260, type: "private",    branch: "CS, IT" },
  { name: "MIT COE Pune",    lat: 18.4967, lng: 73.8789, type: "private",    branch: "CS, Mech, Civil" },
  { name: "PICT Pune",       lat: 18.4573, lng: 73.8493, type: "private",    branch: "CS, ENTC, IT" },
];

function initMap() {
  if (mapInstance) return;
  mapInstance = L.map("college-map").setView([18.52, 73.86], 12);
  L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
    attribution: "© OpenStreetMap",
    maxZoom: 18,
  }).addTo(mapInstance);
  addMarkersToMap(SAMPLE_LOCATIONS);
}

function addMarkersToMap(locations) {
  locations.forEach(loc => {
    const color = loc.type === "government" ? "#34d399" : "#38bdf8";
    const icon = L.divIcon({
      className: "",
      html: `<div style="background:${color};color:#0a0d14;padding:4px 10px;border-radius:100px;
             font-size:0.7rem;font-weight:700;white-space:nowrap;box-shadow:0 2px 8px rgba(0,0,0,0.4);
             font-family:'DM Sans',sans-serif;">${loc.name}</div>`,
      iconAnchor: [0, 0],
    });
    L.marker([loc.lat, loc.lng], { icon })
      .addTo(mapInstance)
      .bindPopup(`<div style="font-family:'DM Sans',sans-serif;min-width:180px">
        <strong>${loc.name}</strong><br/>
        <span style="color:#64748b;font-size:0.85em">Type: ${loc.type}</span><br/>
        <span style="color:#64748b;font-size:0.85em">Branches: ${loc.branch || "Multiple"}</span>
      </div>`);
  });
}

function updateMapMarkers(colleges) {
  if (!mapInstance) initMap();
  const locs = (colleges || [])
    .filter(c => c.latitude && c.longitude)
    .map(c => ({ name: c.name, lat: c.latitude, lng: c.longitude, type: c.type, branch: c.branch }));
  if (locs.length) addMarkersToMap(locs);
}

function showCollegeOnMap(lat, lng, name) {
  if (!mapInstance) initMap();
  scrollToSection("map-section");
  setTimeout(() => mapInstance.flyTo([lat, lng], 14, { duration: 1.5 }), 500);
}

const mapObserver = new IntersectionObserver(entries => {
  if (entries[0].isIntersecting) { initMap(); mapObserver.disconnect(); }
}, { threshold: 0.3 });

document.addEventListener("DOMContentLoaded", () => {
  const mapEl = document.getElementById("college-map");
  if (mapEl) mapObserver.observe(mapEl);
});

// ─────────────────────────────────────────────────────────────────
// BRANCH GUIDANCE
// ─────────────────────────────────────────────────────────────────

function toggleQuizItem(element, key) {
  element.classList.toggle("selected");
  quizAnswers[key] = element.classList.contains("selected");
  const input = element.querySelector("input[type='hidden']");
  if (input) input.value = String(quizAnswers[key]);
}

async function handleBranchGuidance() {
  showLoading("Finding your ideal branch…");

  const answers = {
    likes_coding:           quizAnswers["likes_coding"]           || false,
    likes_ai:               quizAnswers["likes_ai"]               || false,
    likes_electronics:      quizAnswers["likes_electronics"]      || false,
    likes_mechanics:        quizAnswers["likes_mechanics"]        || false,
    prefers_software:       quizAnswers["prefers_software"]       || false,
    likes_design:           quizAnswers["likes_design"]           || false,
    interested_in_research: quizAnswers["interested_in_research"] || false,
  };

  try {
    const data = await apiPost("/branch-guidance", answers);
    const container = document.getElementById("branch-cards-container");
    const rankLabels = ["#1 Best Match", "#2 Strong Fit", "#3 Also Good"];

    container.innerHTML = (data.recommendations || []).map((rec, i) => `
      <div class="branch-card" style="animation-delay:${i * 0.1}s">
        <div class="branch-card-rank">${rankLabels[i] || `#${i + 1}`}</div>
        <div class="branch-card-name">${rec.branch}</div>
        <div class="branch-match-bar">
          <div class="branch-match-fill" style="width:${rec.match_score}%"></div>
        </div>
        <div class="branch-match-pct">${rec.match_score}% match</div>
        <div class="branch-reason">${rec.reason}</div>
      </div>
    `).join("");

    document.getElementById("branch-results").style.display = "block";
    document.getElementById("branch-results").scrollIntoView({ behavior: "smooth" });

  } catch (error) {
    alert(`Branch guidance error: ${error.message}`);
  } finally {
    hideLoading();
  }
}

// ─────────────────────────────────────────────────────────────────
// AI CHATBOT
// ─────────────────────────────────────────────────────────────────

async function sendChatMessage() {
  const input   = document.getElementById("chat-input");
  const message = input.value.trim();
  if (!message) return;

  appendChatMessage(message, "user");
  input.value = "";

  const typingId = appendTypingIndicator();

  const studentContext = {
    percentage:       document.getElementById("student-pct")?.value      || null,
    category:         document.getElementById("student-category")?.value || null,
    preferred_branch: document.getElementById("student-branch")?.value   || null,
  };

  try {
    const data = await apiPost("/chat", { message, student_context: studentContext });
    removeTypingIndicator(typingId);
    appendChatMessage(data.answer, "bot");
  } catch (error) {
    removeTypingIndicator(typingId);
    appendChatMessage(
      `⚠️ Could not reach the AI counselor.<br>
       <em style="opacity:0.7;font-size:0.85em">${error.message}</em>`,
      "bot"
    );
  }
}

function appendChatMessage(text, sender) {
  const messagesDiv = document.getElementById("chat-messages");
  const isBot = sender === "bot";
  const el = document.createElement("div");
  el.className = `chat-message ${isBot ? "bot-message" : "user-message"}`;
  el.innerHTML = `
    ${isBot ? '<div class="bot-avatar">&#129302;</div>' : ""}
    <div class="message-bubble"><p>${text.replace(/\n/g, "<br/>")}</p></div>
  `;
  messagesDiv.appendChild(el);
  messagesDiv.scrollTop = messagesDiv.scrollHeight;
  return el;
}

function appendTypingIndicator() {
  const id = "typing-" + Date.now();
  const messagesDiv = document.getElementById("chat-messages");
  const el = document.createElement("div");
  el.id = id;
  el.className = "chat-message bot-message";
  el.innerHTML = `
    <div class="bot-avatar">&#129302;</div>
    <div class="message-bubble" style="opacity:0.6"><p>&#8226;&#8226;&#8226; thinking…</p></div>
  `;
  messagesDiv.appendChild(el);
  messagesDiv.scrollTop = messagesDiv.scrollHeight;
  return id;
}

function removeTypingIndicator(id) {
  document.getElementById(id)?.remove();
}

function handleChatKeypress(event) {
  if (event.key === "Enter" && !event.shiftKey) {
    event.preventDefault();
    sendChatMessage();
  }
}

function askSampleQuestion(question) {
  document.getElementById("chat-input").value = question;
  document.getElementById("chat-input").focus();
}

// ─────────────────────────────────────────────────────────────────
// PAGE INIT
// ─────────────────────────────────────────────────────────────────

document.addEventListener("DOMContentLoaded", () => {
  console.log("🎓 CollegePath AI v2 loaded");

  // Navbar scroll effect
  window.addEventListener("scroll", () => {
    const navbar = document.querySelector(".navbar");
    navbar.style.background = window.scrollY > 20
      ? "rgba(10,13,20,0.97)"
      : "rgba(10,13,20,0.85)";
  });

  // Drag & drop for both upload zones
  setupDragDrop("marksheet-zone", "marksheet-input");
  setupDragDrop("cutoff-zone",    "cutoff-input");
});

function setupDragDrop(zoneId, inputId) {
  const zone = document.getElementById(zoneId);
  if (!zone) return;

  zone.addEventListener("dragover", e => {
    e.preventDefault();
    zone.style.borderColor = "var(--accent)";
    zone.style.background  = "rgba(56,189,248,0.06)";
  });

  zone.addEventListener("dragleave", () => {
    zone.style.borderColor = "";
    zone.style.background  = "";
  });

  zone.addEventListener("drop", e => {
    e.preventDefault();
    zone.style.borderColor = "";
    zone.style.background  = "";

    const file = e.dataTransfer.files[0];
    if (!file) return;

    // Inject file into hidden input and fire change event
    const input = document.getElementById(inputId);
    const dt = new DataTransfer();
    dt.items.add(file);
    input.files = dt.files;
    input.dispatchEvent(new Event("change"));
  });
}