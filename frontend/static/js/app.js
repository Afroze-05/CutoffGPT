/* CollegePath AI — Main App JS */
const API = '';
let sessionId = localStorage.getItem('cpai_session');
let currentResults = { dream: [], target: [], safe: [], summary: '' };
let compareColleges = [];
let allColleges = [];
let map = null;
let mapMarkers = [];
let quizAnswers = {};
let quizIndex = 0;
let quizQuestions = [];
let branchChatHistory = [];

/* ── INIT ── */
document.addEventListener('DOMContentLoaded', async () => {
  await initSession();
  await loadCollegesForCompare();
  initBranchQuiz();
  initMap();
  loadNavTabHandlers();
});

async function initSession() {
  if (!sessionId) {
    const res = await api('POST', '/api/student/session/new');
    sessionId = res.data.session_id;
    localStorage.setItem('cpai_session', sessionId);
  } else {
    // Restore session state
    try {
      const res = await api('GET', `/api/student/session/${sessionId}`);
      if (res.data) restoreSession(res.data);
    } catch {
      // Session expired — create new
      const res = await api('POST', '/api/student/session/new');
      sessionId = res.data.session_id;
      localStorage.setItem('cpai_session', sessionId);
    }
  }
}

function restoreSession(data) {
  if (data.student_info?.percentile || data.student_info?.percentage) {
    updateProfileDisplay(data.student_info);
    enableChat();
  }
  if (data.has_recommendations) {
    // Show go-to-results hint
    document.getElementById('getRecoBtn').style.display = 'block';
  }
}

/* ── NAVIGATION ── */
function loadNavTabHandlers() {
  document.querySelectorAll('.nav-tab').forEach(btn => {
    btn.addEventListener('click', () => showTab(btn.dataset.tab));
  });
}

function showTab(tab) {
  document.querySelectorAll('.page').forEach(p => p.classList.remove('active'));
  document.querySelectorAll('.nav-tab').forEach(b => b.classList.remove('active'));
  document.getElementById(`page-${tab}`).classList.add('active');
  document.querySelector(`[data-tab="${tab}"]`)?.classList.add('active');
  if (tab === 'map') setTimeout(initMap, 100);
}

function startJourney() { showTab('chat'); }

/* ── MARKSHEET UPLOAD ── */
async function handleMarksheetUpload(event) {
  const file = event.target.files[0];
  if (!file) return;
  showLoading('Analyzing your marksheet with AI... 🔍');

  const formData = new FormData();
  formData.append('session_id', sessionId);
  formData.append('file', file);

  try {
    const res = await fetch(`${API}/api/student/upload-marksheet`, { method: 'POST', body: formData });
    const data = await res.json();
    hideLoading();

    if (data.success) {
      updateProfileDisplay(data.data.student_info);
      appendMessage(data.data.greeting, 'ai');
      enableChat();
      updateUploadZone(file.name);
    } else {
      alert('Failed to process marksheet. Please try manually.');
    }
  } catch (e) {
    hideLoading();
    alert('Upload failed. Please check your connection.');
  }
}

async function submitManualProfile() {
  const exam = document.getElementById('manualExam').value;
  const percentile = parseFloat(document.getElementById('manualPercentile').value) || null;
  const percentage = parseFloat(document.getElementById('manualPercentage').value) || null;
  const category = document.getElementById('manualCategory').value;
  const name = document.getElementById('manualName').value;

  if (!percentile && !percentage) {
    alert('Please enter your percentile or percentage.');
    return;
  }

  showLoading('Setting up your profile...');
  const formData = new FormData();
  formData.append('session_id', sessionId);
  formData.append('exam_type', exam);
  if (percentile) formData.append('percentile', percentile);
  if (percentage) formData.append('percentage', percentage);
  formData.append('category', category);
  formData.append('student_name', name);

  try {
    const res = await fetch(`${API}/api/student/manual-profile`, { method: 'POST', body: formData });
    const data = await res.json();
    hideLoading();

    if (data.success) {
      updateProfileDisplay({ exam_type: exam, percentile, percentage, category, student_name: name });
      appendMessage(data.data.greeting, 'ai');
      enableChat();
    }
  } catch (e) {
    hideLoading();
    alert('Failed to set profile.');
  }
}

/* ── CHAT ── */
async function sendChat() {
  const input = document.getElementById('chatInput');
  const msg = input.value.trim();
  if (!msg) return;

  input.value = '';
  appendMessage(msg, 'user');
  showTyping();
  document.getElementById('sendBtn').disabled = true;

  try {
    const res = await api('POST', '/api/student/chat', { session_id: sessionId, message: msg });
    hideTyping();
    appendMessage(res.response, 'ai');
    updatePrefsDisplay(res.updated_preferences);

    if (res.preferences_complete) {
      document.getElementById('getRecoBtn').style.display = 'block';
      document.getElementById('chatStatus').textContent = 'Preferences collected ✅';
    }
  } catch (e) {
    hideTyping();
    appendMessage('Sorry, I had trouble responding. Please try again.', 'ai');
  }
  document.getElementById('sendBtn').disabled = false;
}

function handleChatKey(e) {
  if (e.key === 'Enter') sendChat();
}

function enableChat() {
  document.getElementById('chatInput').disabled = false;
  document.getElementById('sendBtn').disabled = false;
  document.getElementById('chatStatus').textContent = 'Online — Ask me anything!';
}

function appendMessage(text, role) {
  const container = document.getElementById('chatMessages');
  const div = document.createElement('div');
  div.className = `msg ${role}`;
  div.innerHTML = `<div class="msg-bubble">${formatMessage(text)}</div>`;
  container.appendChild(div);
  container.scrollTop = container.scrollHeight;
}

function formatMessage(text) {
  return text
    .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
    .replace(/\*(.*?)\*/g, '<em>$1</em>')
    .replace(/\n/g, '<br>');
}

function showTyping() {
  const container = document.getElementById('chatMessages');
  const div = document.createElement('div');
  div.className = 'msg ai';
  div.id = 'typingIndicator';
  div.innerHTML = '<div class="msg-bubble"><div class="typing-indicator"><div class="dot"></div><div class="dot"></div><div class="dot"></div></div></div>';
  container.appendChild(div);
  container.scrollTop = container.scrollHeight;
}

function hideTyping() {
  document.getElementById('typingIndicator')?.remove();
}

/* ── RECOMMENDATIONS ── */
async function getRecommendations() {
  showLoading('AI is analyzing your profile and matching colleges... 🤖');
  try {
    const res = await api('POST', '/api/student/recommendations', { session_id: sessionId });
    hideLoading();
    currentResults = res.data;
    showTab('results');
    renderResults('target');
    document.getElementById('resultsSummary').textContent = res.data.summary;
  } catch (e) {
    hideLoading();
    alert('Failed to generate recommendations. Please try again.');
  }
}

function showResultTab(tier) {
  document.querySelectorAll('.rtab').forEach(t => t.classList.remove('active'));
  document.querySelector(`[data-rtab="${tier}"]`).classList.add('active');
  renderResults(tier);
}

function renderResults(tier) {
  const colleges = currentResults[tier] || [];
  const container = document.getElementById('resultsContainer');

  if (!colleges.length) {
    container.innerHTML = `<div class="empty-state"><p>No ${tier} colleges found for your profile.</p></div>`;
    return;
  }

  container.innerHTML = colleges.map(c => `
    <div class="college-card ${tier}">
      <div class="card-tier ${tier}">${tier === 'dream' ? '🌟 Dream' : tier === 'target' ? '🎯 Target' : '✅ Safe'}</div>
      <div class="card-college-name">${c.college_name || ''}</div>
      <div class="card-branch">${c.branch_name || ''}</div>
      <div class="card-prob ${tier}">${c.probability_percent ? Math.round(c.probability_percent) + '%' : '—'}</div>
      <div class="card-prob-label">Admission Probability</div>
      <div class="card-stats">
        <div class="card-stat">
          <div class="card-stat-val">${c.cutoff_percentile ? c.cutoff_percentile + '%ile' : '—'}</div>
          <div class="card-stat-label">Cutoff (OPEN)</div>
        </div>
        <div class="card-stat">
          <div class="card-stat-val">${c.annual_fees ? '₹' + Math.round(c.annual_fees/1000) + 'K' : '—'}</div>
          <div class="card-stat-label">Annual Fees</div>
        </div>
        <div class="card-stat">
          <div class="card-stat-val">${c.avg_placement_lpa ? c.avg_placement_lpa + ' LPA' : '—'}</div>
          <div class="card-stat-label">Avg Placement</div>
        </div>
        <div class="card-stat">
          <div class="card-stat-val">${c.city || '—'}</div>
          <div class="card-stat-label">City</div>
        </div>
      </div>
      ${c.reason ? `<div class="card-reason">${c.reason}</div>` : ''}
      <div class="card-tags">
        ${c.college_type ? `<span class="tag tag-blue">${c.college_type}</span>` : ''}
        ${c.hostel_available ? '<span class="tag tag-green">🏠 Hostel</span>' : ''}
        ${(c.pros || []).slice(0,2).map(p => `<span class="tag tag-green">✓ ${p}</span>`).join('')}
        ${(c.cons || []).slice(0,1).map(p => `<span class="tag tag-red">✗ ${p}</span>`).join('')}
      </div>
    </div>
  `).join('');
}

/* ── COMPARE ── */
async function loadCollegesForCompare() {
  try {
    const res = await api('GET', '/api/admin/colleges');
    allColleges = res.data || [];
  } catch (e) {
    allColleges = [];
  }
}

function searchColleges(query) {
  const dropdown = document.getElementById('searchDropdown');
  if (!query || query.length < 2) { dropdown.style.display = 'none'; return; }

  const matches = allColleges.filter(c =>
    c.name.toLowerCase().includes(query.toLowerCase()) ||
    (c.short_name || '').toLowerCase().includes(query.toLowerCase())
  ).slice(0, 6);

  if (!matches.length) { dropdown.style.display = 'none'; return; }

  dropdown.innerHTML = matches.map(c => `
    <div class="search-item" onclick="addCompareCollege('${c.name}', '${c.short_name || c.name}')">
      <strong>${c.short_name || ''}</strong> — ${c.name}
    </div>
  `).join('');
  dropdown.style.display = 'block';
}

function addCompareCollege(name, shortName) {
  if (compareColleges.length >= 4) { alert('Max 4 colleges'); return; }
  if (compareColleges.includes(name)) return;
  compareColleges.push(name);
  document.getElementById('searchDropdown').style.display = 'none';
  document.getElementById('compareSearchInput').value = '';
  renderCompareTags();
}

function removeCompareCollege(name) {
  compareColleges = compareColleges.filter(c => c !== name);
  renderCompareTags();
}

function renderCompareTags() {
  document.getElementById('compareCollegeTags').innerHTML = compareColleges.map(c => `
    <div class="college-tag">
      ${c.split(',')[0]}
      <span class="college-tag-remove" onclick="removeCompareCollege('${c}')">×</span>
    </div>
  `).join('');
}

async function runComparison() {
  if (compareColleges.length < 2) { alert('Please select at least 2 colleges'); return; }
  showLoading('Comparing colleges with AI... ⚖️');

  try {
    const res = await api('POST', '/api/student/compare', {
      session_id: sessionId,
      college_names: compareColleges,
    });
    hideLoading();
    renderComparison(res);
  } catch (e) {
    hideLoading();
    alert('Comparison failed. Please try again.');
  }
}

function renderComparison(data) {
  const { colleges, comparison_table, ai_verdict } = data;
  const container = document.getElementById('comparisonResult');

  const headers = colleges.map(c => `<th>${c.short_name || c.name.split(' ')[0]}<br><small style="font-weight:400;color:#64748b">${c.city}</small></th>`).join('');
  const rows = (comparison_table || []).map(row => `
    <tr>
      <td class="feature-col">${row.feature}</td>
      ${(row.values || []).map(v => `<td>${v}</td>`).join('')}
    </tr>
  `).join('');

  const verdictHtml = ai_verdict ? `
    <div class="verdict-card" style="margin-top:20px">
      <h3>🤖 AI Verdict</h3>
      <div class="verdict-badges">
        ${ai_verdict.best_for_placement ? `<div class="verdict-badge">🏆 Best Placement: ${ai_verdict.best_for_placement}</div>` : ''}
        ${ai_verdict.best_for_budget ? `<div class="verdict-badge">💰 Best Budget: ${ai_verdict.best_for_budget}</div>` : ''}
        ${ai_verdict.best_for_student ? `<div class="verdict-badge">⭐ Best for You: ${ai_verdict.best_for_student}</div>` : ''}
      </div>
      <p style="font-size:.9rem;opacity:.9">${ai_verdict.verdict_reason || ''}</p>
    </div>
  ` : '';

  container.innerHTML = `
    <div class="compare-table-wrap">
      <table class="compare-table">
        <thead><tr><th>Feature</th>${headers}</tr></thead>
        <tbody>${rows}</tbody>
      </table>
    </div>
    ${verdictHtml}
  `;
}

/* ── MAP ── */
async function initMap() {
  if (map) return;
  const el = document.getElementById('mapContainer');
  if (!el || !el.offsetParent) return;

  map = L.map('mapContainer').setView([18.5204, 73.8567], 8);
  L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    attribution: '© OpenStreetMap contributors'
  }).addTo(map);

  await loadMapColleges();
}

async function loadMapColleges() {
  if (!allColleges.length) await loadCollegesForCompare();

  const listEl = document.getElementById('mapCollegeList');
  listEl.innerHTML = '';
  mapMarkers.forEach(m => m.remove());
  mapMarkers = [];

  allColleges.forEach(college => {
    if (!college.latitude || !college.longitude) return;

    const icon = L.divIcon({
      html: `<div style="background:${college.college_type === 'Government' ? '#10b981' : '#6366f1'};color:white;padding:3px 8px;border-radius:20px;font-size:11px;font-weight:700;white-space:nowrap;box-shadow:0 2px 6px rgba(0,0,0,.2)">${college.short_name || college.name.split(' ')[0]}</div>`,
      className: '',
      iconAnchor: [20, 10],
    });

    const marker = L.marker([college.latitude, college.longitude], { icon })
      .addTo(map)
      .bindPopup(`
        <strong>${college.name}</strong><br>
        <span style="color:#64748b">${college.city} • ${college.college_type}</span><br>
        Fees: ₹${college.annual_fees ? Math.round(college.annual_fees/1000) + 'K/yr' : 'N/A'}<br>
        Avg Placement: ${college.avg_placement_lpa ? college.avg_placement_lpa + ' LPA' : 'N/A'}
      `);
    mapMarkers.push(marker);

    const item = document.createElement('div');
    item.className = 'map-college-item';
    item.innerHTML = `
      <h4>${college.short_name || college.name}</h4>
      <p>${college.city} • ${college.college_type} • ${college.naac_grade ? 'NAAC ' + college.naac_grade : ''}</p>
    `;
    item.onclick = () => {
      map.setView([college.latitude, college.longitude], 13);
      marker.openPopup();
    };
    listEl.appendChild(item);
  });
}

async function filterMapColleges() {
  const typeFilter = document.getElementById('mapTypeFilter').value;
  const cityFilter = document.getElementById('mapCityFilter').value;

  const filtered = allColleges.filter(c => {
    if (typeFilter && c.college_type !== typeFilter) return false;
    if (cityFilter && c.city !== cityFilter) return false;
    return true;
  });

  const listEl = document.getElementById('mapCollegeList');
  listEl.innerHTML = '';
  mapMarkers.forEach(m => m.remove());
  mapMarkers = [];

  filtered.forEach(college => {
    if (!college.latitude || !college.longitude) return;
    const marker = L.marker([college.latitude, college.longitude])
      .addTo(map)
      .bindPopup(`<strong>${college.name}</strong><br>${college.city}`);
    mapMarkers.push(marker);

    const item = document.createElement('div');
    item.className = 'map-college-item';
    item.innerHTML = `<h4>${college.short_name || college.name}</h4><p>${college.city} • ${college.college_type}</p>`;
    item.onclick = () => { map.setView([college.latitude, college.longitude], 13); marker.openPopup(); };
    listEl.appendChild(item);
  });
}

/* ── BRANCH QUIZ ── */
async function initBranchQuiz() {
  try {
    const res = await api('GET', '/api/branch/questions');
    quizQuestions = res.data || [];
    renderQuizQuestion();
  } catch (e) {
    document.getElementById('branchQuiz').innerHTML = '<p class="muted">Could not load quiz. Please try again.</p>';
  }
}

function renderQuizQuestion() {
  if (quizIndex >= quizQuestions.length) {
    submitBranchQuiz();
    return;
  }
  const q = quizQuestions[quizIndex];
  const fill = ((quizIndex) / quizQuestions.length) * 100;
  document.getElementById('quizFill').style.width = fill + '%';
  document.getElementById('quizProgress').textContent = `Question ${quizIndex + 1} of ${quizQuestions.length}`;

  document.getElementById('quizContent').innerHTML = `
    <div class="quiz-question">${q.question}</div>
    <div class="quiz-options">
      ${q.options.map(opt => `
        <button class="quiz-option" onclick="selectOption('${q.id}', '${opt}', this)">${opt}</button>
      `).join('')}
    </div>
  `;
}

function selectOption(id, value, btn) {
  document.querySelectorAll('.quiz-option').forEach(b => b.classList.remove('selected'));
  btn.classList.add('selected');
  quizAnswers[id] = value;
  setTimeout(() => {
    quizIndex++;
    renderQuizQuestion();
  }, 400);
}

async function submitBranchQuiz() {
  document.getElementById('branchQuiz').innerHTML = '<div style="text-align:center;padding:32px"><div class="spinner" style="margin:0 auto"></div><p style="margin-top:12px">AI is analyzing your interests...</p></div>';

  try {
    const res = await api('POST', '/api/branch/recommend', quizAnswers);
    renderBranchResults(res.data);
  } catch (e) {
    document.getElementById('branchQuiz').innerHTML = '<p class="muted">Analysis failed. Please refresh and try again.</p>';
  }
}

function renderBranchResults(data) {
  document.getElementById('branchQuiz').style.display = 'none';
  const container = document.getElementById('branchResults');
  container.style.display = 'block';

  const recs = data.recommendations || [];
  container.innerHTML = `
    <div style="text-align:center;margin-bottom:24px">
      <h3 style="font-size:1.4rem;font-weight:800">Your Top Branch: <span style="color:var(--primary)">${data.top_branch}</span></h3>
      <p style="color:var(--text2)">${data.overall_advice || ''}</p>
    </div>
    <div class="branch-results-grid">
      ${recs.map((r, i) => `
        <div class="branch-card ${i === 0 ? 'top' : ''}">
          ${i === 0 ? '<div style="font-size:.75rem;font-weight:700;color:var(--primary);margin-bottom:4px">⭐ BEST MATCH</div>' : ''}
          <div class="branch-match">${r.match_percent}%</div>
          <div class="branch-name">${r.branch}</div>
          <div class="branch-why">${r.why}</div>
          <div style="font-size:.78rem;color:var(--text2);margin-bottom:8px">Scope: ${r.scope || 'Good'}</div>
          <div style="font-size:.78rem;font-weight:600;color:var(--secondary);margin-bottom:8px">Salary: ${r.avg_salary_range || 'N/A'}</div>
          <div class="branch-careers">
            ${(r.career_paths || []).map(c => `<span class="tag tag-blue">${c}</span>`).join('')}
          </div>
        </div>
      `).join('')}
    </div>
    ${data.avoid_branches?.length ? `
      <div class="alert alert-info">
        ⚠️ <strong>Consider avoiding:</strong> ${data.avoid_branches.join(', ')} — ${data.avoid_reason}
      </div>
    ` : ''}
    <div style="text-align:center;margin-top:20px">
      <button class="btn-secondary" onclick="restartQuiz()">🔄 Retake Quiz</button>
    </div>
  `;
}

function restartQuiz() {
  quizAnswers = {};
  quizIndex = 0;
  document.getElementById('branchResults').style.display = 'none';
  document.getElementById('branchQuiz').style.display = 'block';
  renderQuizQuestion();
}

/* ── BRANCH CHAT ── */
async function sendBranchChat() {
  const input = document.getElementById('branchChatInput');
  const msg = input.value.trim();
  if (!msg) return;
  input.value = '';

  appendBranchMessage(msg, 'user');

  try {
    const res = await api('POST', '/api/branch/chat', { message: msg, history: branchChatHistory });
    appendBranchMessage(res.data.response, 'ai');
    branchChatHistory.push({ role: 'user', content: msg });
    branchChatHistory.push({ role: 'assistant', content: res.data.response });
    branchChatHistory = branchChatHistory.slice(-12);
  } catch (e) {
    appendBranchMessage('Sorry, I could not process that. Please try again.', 'ai');
  }
}

function appendBranchMessage(text, role) {
  const container = document.getElementById('branchChatMessages');
  const div = document.createElement('div');
  div.className = `msg ${role}`;
  div.innerHTML = `<div class="msg-bubble">${formatMessage(text)}</div>`;
  container.appendChild(div);
  container.scrollTop = container.scrollHeight;
}

/* ── HELPERS ── */
function updateProfileDisplay(info) {
  const el = document.getElementById('profileDisplay');
  const rows = [
    ['Name', info.student_name || '—'],
    ['Exam', info.exam_type || '—'],
    ['Percentile', info.percentile ? info.percentile + '%ile' : '—'],
    ['Percentage', info.percentage ? info.percentage + '%' : '—'],
    ['Rank', info.rank || '—'],
    ['Category', info.category || 'OPEN'],
  ].filter(([, v]) => v !== '—');

  el.innerHTML = rows.map(([k, v]) => `
    <div class="profile-row"><span class="profile-key">${k}</span><span class="profile-val">${v}</span></div>
  `).join('');
}

function updatePrefsDisplay(prefs) {
  const card = document.getElementById('prefCard');
  const el = document.getElementById('prefDisplay');
  card.style.display = 'block';

  const items = Object.entries(prefs).filter(([, v]) => v && v !== '' && (!Array.isArray(v) || v.length));
  el.innerHTML = items.map(([k, v]) => `
    <div class="pref-item">
      <span class="pref-icon">✅</span>
      <span><strong>${k.replace(/_/g, ' ')}:</strong> ${Array.isArray(v) ? v.join(', ') : v}</span>
    </div>
  `).join('');
}

function updateUploadZone(filename) {
  const zone = document.getElementById('uploadZone');
  zone.innerHTML = `<div class="upload-icon">✅</div><p>${filename}</p><span class="upload-hint">Successfully analyzed</span>`;
  zone.style.borderColor = 'var(--secondary)';
  zone.style.background = '#f0fdf4';
}

async function api(method, path, body) {
  const opts = {
    method,
    headers: { 'Content-Type': 'application/json' },
  };
  if (body) opts.body = JSON.stringify(body);
  const res = await fetch(`${API}${path}`, opts);
  if (!res.ok) throw new Error(`API error: ${res.status}`);
  return res.json();
}

function showLoading(msg) {
  document.getElementById('loadingMsg').textContent = msg || 'Loading...';
  document.getElementById('loadingOverlay').style.display = 'flex';
}

function hideLoading() {
  document.getElementById('loadingOverlay').style.display = 'none';
}
