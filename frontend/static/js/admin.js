/* CollegePath AI — Admin JS */
const API = '';

document.addEventListener('DOMContentLoaded', () => {
  loadStats();
  loadUploads();
  loadColleges();
  loadCutoffs();
});

async function api(method, path, body) {
  const opts = { method, headers: { 'Content-Type': 'application/json' } };
  if (body) opts.body = JSON.stringify(body);
  const res = await fetch(`${API}${path}`, opts);
  if (!res.ok) throw new Error(`API ${res.status}`);
  return res.json();
}

function showLoading(msg) {
  document.getElementById('loadingMsg').textContent = msg || 'Processing...';
  document.getElementById('loadingOverlay').style.display = 'flex';
}

function hideLoading() {
  document.getElementById('loadingOverlay').style.display = 'none';
}

async function loadStats() {
  try {
    const res = await api('GET', '/api/admin/stats');
    document.getElementById('sColleges').textContent = res.data.colleges;
    document.getElementById('sBranches').textContent = res.data.branches;
    document.getElementById('sCutoffs').textContent = res.data.cutoff_records;
    document.getElementById('sUploads').textContent = res.data.uploads;
  } catch (e) {
    console.error('Stats load failed', e);
  }
}

async function seedDatabase() {
  showLoading('Seeding database with Maharashtra college data...');
  const resultEl = document.getElementById('seedResult');
  try {
    const res = await api('POST', '/api/admin/seed');
    hideLoading();
    resultEl.className = 'alert alert-success';
    resultEl.textContent = `✅ Seeded: ${res.data.colleges_added} colleges, ${res.data.branches_added} branches, ${res.data.cutoffs_added} cutoff records`;
    resultEl.style.display = 'block';
    loadStats();
    loadColleges();
    loadCutoffs();
  } catch (e) {
    hideLoading();
    resultEl.className = 'alert alert-error';
    resultEl.textContent = '❌ Seeding failed. Check console.';
    resultEl.style.display = 'block';
  }
}

async function handleCutoffUpload(event) {
  const file = event.target.files[0];
  if (!file) return;

  const examType = document.getElementById('uploadExamType').value;
  const year = document.getElementById('uploadYear').value;
  const resultEl = document.getElementById('uploadResult');

  showLoading(`Uploading and processing ${file.name}...`);

  const formData = new FormData();
  formData.append('file', file);
  formData.append('exam_type', examType);
  formData.append('year', year);

  try {
    const res = await fetch(`${API}/api/admin/upload-cutoff-pdf`, { method: 'POST', body: formData });
    const data = await res.json();
    hideLoading();

    resultEl.className = 'alert alert-info';
    resultEl.textContent = `📁 Upload #${data.upload_id}: ${data.message}`;
    resultEl.style.display = 'block';
    loadUploads();
    loadStats();
  } catch (e) {
    hideLoading();
    resultEl.className = 'alert alert-error';
    resultEl.textContent = '❌ Upload failed. File may be too large or invalid.';
    resultEl.style.display = 'block';
  }
}

async function loadUploads() {
  try {
    const res = await api('GET', '/api/admin/uploads');
    const tbody = document.getElementById('uploadsBody');
    if (!res.data?.length) {
      tbody.innerHTML = '<tr><td colspan="6" class="muted center">No uploads yet</td></tr>';
      return;
    }
    tbody.innerHTML = res.data.map(u => `
      <tr>
        <td>${u.id}</td>
        <td title="${u.filename}">${u.filename?.substring(0, 40)}${u.filename?.length > 40 ? '...' : ''}</td>
        <td>${u.file_type}</td>
        <td><span class="badge badge-${u.status}">${u.status}</span></td>
        <td>${u.records_extracted || 0}</td>
        <td>${u.created_at ? new Date(u.created_at).toLocaleDateString() : '—'}</td>
      </tr>
    `).join('');
  } catch (e) {
    document.getElementById('uploadsBody').innerHTML = '<tr><td colspan="6" class="muted center">Load failed</td></tr>';
  }
}

async function loadColleges() {
  try {
    const res = await api('GET', '/api/admin/colleges');
    const tbody = document.getElementById('collegesBody');
    if (!res.data?.length) {
      tbody.innerHTML = '<tr><td colspan="7" class="muted center">No colleges. Click "Seed Sample Data".</td></tr>';
      return;
    }
    tbody.innerHTML = res.data.map(c => `
      <tr>
        <td><strong>${c.short_name || ''}</strong><br><small style="color:#64748b">${c.name}</small></td>
        <td>${c.city || '—'}</td>
        <td><span class="badge ${c.college_type === 'Government' ? 'badge-done' : 'badge-pending'}">${c.college_type || '—'}</span></td>
        <td>${c.naac_grade || '—'}</td>
        <td>${c.annual_fees ? '₹' + Math.round(c.annual_fees/1000) + 'K' : '—'}</td>
        <td>${c.avg_placement_lpa ? c.avg_placement_lpa + ' LPA' : '—'}</td>
        <td>${c.hostel_available ? '✅' : '❌'}</td>
      </tr>
    `).join('');
  } catch (e) {
    document.getElementById('collegesBody').innerHTML = '<tr><td colspan="7" class="muted center">Load failed</td></tr>';
  }
}

async function loadCutoffs() {
  const search = document.getElementById('cutoffSearch')?.value || '';
  try {
    const url = search ? `/api/admin/cutoffs?college_name=${encodeURIComponent(search)}` : '/api/admin/cutoffs';
    const res = await api('GET', url);
    const tbody = document.getElementById('cutoffsBody');
    if (!res.data?.length) {
      tbody.innerHTML = '<tr><td colspan="7" class="muted center">No records. Seed data or upload PDFs.</td></tr>';
      return;
    }
    tbody.innerHTML = res.data.slice(0, 100).map(r => `
      <tr>
        <td>${r.college_name}</td>
        <td>${r.branch_name}</td>
        <td>${r.exam_type}</td>
        <td>${r.year}</td>
        <td>${r.round_no}</td>
        <td><span class="badge badge-pending">${r.category}</span></td>
        <td><strong>${r.cutoff_percentile ? r.cutoff_percentile + '%ile' : r.cutoff_rank ? 'Rank ' + r.cutoff_rank : '—'}</strong></td>
      </tr>
    `).join('');
  } catch (e) {
    document.getElementById('cutoffsBody').innerHTML = '<tr><td colspan="7" class="muted center">Load failed</td></tr>';
  }
}
