// Basic frontend logic: Local auth, analyze upload, video creation, history listing

// Simple local authentication - no Firebase needed
let currentUser = null;

function getCurrentUser() {
  if (!currentUser) {
    const userId = localStorage.getItem('userId');
    if (userId) {
      currentUser = { uid: userId, email: `user_${userId.slice(0,8)}@local` };
    } else {
      currentUser = { uid: 'local_user_' + Date.now(), email: 'local@user.com' };
      localStorage.setItem('userId', currentUser.uid);
    }
  }
  return currentUser;
}

async function getIdToken() {
  // For local storage, we don't need tokens
  return 'local-auth';
}

function qs(id) { return document.getElementById(id); }

function show(el) { el.classList.remove('d-none'); }
function hide(el) { el.classList.add('d-none'); }

// Simple local auth - always show app section
function initializeApp() {
  const authSection = qs('authSection');
  const appSection = qs('appSection');
  const btnLogout = qs('btnLogout');
  
  // Hide auth section, show app section
  if (authSection) hide(authSection);
  if (appSection) show(appSection);
  if (btnLogout) show(btnLogout);
}

// Initialize app on page load
document.addEventListener('DOMContentLoaded', initializeApp);

const btnLogin = qs('btnLogin');
if (btnLogin) {
  btnLogin.addEventListener('click', async () => {
    // For local storage, just initialize the app
    initializeApp();
  });
}

const btnLogout = qs('btnLogout');
if (btnLogout) {
  btnLogout.addEventListener('click', () => {
    // Clear local storage and reload
    localStorage.removeItem('userId');
    location.reload();
  });
}

const btnAnalyze = qs('btnAnalyze');
if (btnAnalyze) {
  btnAnalyze.addEventListener('click', async () => {
    const photo = qs('photo').files[0];
    const shareLocation = qs('shareLocation').checked;
    const analyzeStatus = qs('analyzeStatus');
    analyzeStatus.textContent = 'Analyzing...';
    const token = await getIdToken();
    if (!token) { analyzeStatus.textContent = 'Please login first.'; return; }

    let lat = null, lon = null;
    if (shareLocation && navigator.geolocation) {
      try {
        const pos = await new Promise((resolve, reject) => navigator.geolocation.getCurrentPosition(resolve, reject, {timeout: 8000}));
        lat = pos.coords.latitude; lon = pos.coords.longitude;
      } catch {}
    }

    const form = new FormData();
    if (photo) form.append('photo', photo);
    if (lat != null && lon != null) { form.append('lat', lat); form.append('lon', lon); }

    const resp = await fetch('/api/analyze', {
      method: 'POST',
      headers: { 'Authorization': `Bearer ${token}` },
      body: form
    });
    const data = await resp.json();
    if (!resp.ok) { analyzeStatus.textContent = data.error || 'Error'; return; }
    analyzeStatus.textContent = 'Done.';
    window.__lastAnalysisId = data.id;
    qs('results').textContent = JSON.stringify(data, null, 2);
    const btnMakeVideo = qs('btnMakeVideo');
    btnMakeVideo.classList.remove('d-none');
  });
}

const btnMakeVideo = qs('btnMakeVideo');
if (btnMakeVideo) {
  btnMakeVideo.addEventListener('click', async () => {
    if (!window.__lastAnalysisId) return;
    const token = await getIdToken();
    const resp = await fetch('/api/video', {
      method: 'POST',
      headers: { 'Authorization': `Bearer ${token}`, 'Content-Type': 'application/json' },
      body: JSON.stringify({ analysisId: window.__lastAnalysisId })
    });
    const data = await resp.json();
    if (!resp.ok) { alert(data.error || 'Error creating video'); return; }
    qs('videoResult').innerHTML = `<video controls src="${data.videoUrl}" class="w-100"></video>`;
  });
}

// History page
const historyList = qs('historyList');
if (historyList) {
  // Load history on page load
  async function loadHistory() {
    const user = getCurrentUser();
    if (!user) return;
    const token = await getIdToken();
    const resp = await fetch('/api/history', { headers: { 'Authorization': `Bearer ${token}` } });
    const data = await resp.json();
    if (!resp.ok) return;
    historyList.innerHTML = (data.items || []).map(it => `
      <div class="col-md-4">
        <div class="card h-100">
          <div class="card-body">
            <div class="small text-muted">${it.createdAt}</div>
            <div class="small">pH: ${(it.analysis||{}).pH} | OM: ${(it.analysis||{}).OM} | EC: ${(it.analysis||{}).EC}</div>
            <div class="small">Moisture: ${(it.analysis||{}).moisture}</div>
            <details class="mt-2"><summary>Story</summary><p>${(it.story||'').replace(/</g,'&lt;')}</p></details>
          </div>
          <div class="card-footer">
            ${it.videoUrl ? `<a href="${it.videoUrl}" class="btn btn-sm btn-success" target="_blank">Watch Video</a>` : '<span class="text-muted small">No video</span>'}
          </div>
        </div>
      </div>
    `).join('');
  }
  
  // Load history when page loads
  document.addEventListener('DOMContentLoaded', loadHistory);
}


