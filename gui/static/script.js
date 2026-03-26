/* dookie GUI script */

// ── Wizard navigation ──────────────────────────────────────────────────────
function showStep(prefix, step) {
  [1,2,3].forEach(n => {
    const panel = document.getElementById(`${prefix}-step${n}`);
    const dot   = document.getElementById(`${prefix}-s${n}-dot`);
    if (!panel) return;
    panel.classList.toggle('d-none', n !== step);
    if (dot) {
      dot.classList.toggle('active', n === step);
      dot.classList.toggle('done',   n < step);
    }
  });
}

function bldNext(step) { showStep('bld', step); }
function dirNext(step) {
  // In basic mode, skip step 3 and generate immediately
  const mode = getMode('dir');
  if (step === 3 && mode === 'basic') {
    buildDork('dirs');
    return;
  }
  showStep('dir', step);
}
function ffNext(step) {
  const mode = getMode('ff');
  if (step === 3 && mode === 'basic') {
    buildDork('files');
    return;
  }
  showStep('ff', step);
}

// ── Mode toggle ─────────────────────────────────────────────────────────────
function getMode(prefix) {
  const active = document.querySelector(`#${prefix}-mode .btn-mode.active`);
  return active ? active.dataset.mode : 'basic';
}

function setMode(prefix, btn) {
  document.querySelectorAll(`#${prefix}-mode .btn-mode`).forEach(b => b.classList.remove('active'));
  btn.classList.add('active');
  // Show/hide advanced fields in builder tab
  if (prefix === 'bld') {
    const isAdv = btn.dataset.mode === 'advanced';
    document.getElementById('bld-ops-basic').classList.toggle('d-none', isAdv);
    document.getElementById('bld-ops-advanced').classList.toggle('d-none', !isAdv);
  }
}

// ── Dork builder ─────────────────────────────────────────────────────────────
async function buildDork(tab) {
  let payload = { keywords: [], operators: {}, preset_id: null };

  if (tab === 'builder') {
    const kw = document.getElementById('bld-keywords').value.trim();
    payload.keywords = kw ? kw.split(/\s+/) : [];
    const mode = getMode('bld');
    if (mode === 'basic') {
      const ops = ['site','intitle','filetype','minus'];
      ops.forEach(op => {
        const el = document.getElementById(`bop-${op}`);
        if (el && el.value.trim()) payload.operators[op] = el.value.trim();
      });
    } else {
      document.querySelectorAll('.adv-op-input').forEach(el => {
        if (el.value.trim()) payload.operators[el.dataset.opname] = el.value.trim();
      });
    }
  }

  if (tab === 'dirs') {
    payload.preset_id = document.getElementById('dir-preset').value;
    const mode = getMode('dir');
    if (mode === 'advanced') {
      const kw = document.getElementById('dir-keywords').value.trim();
      payload.keywords = kw ? kw.split(/\s+/) : [];
      ['intitle','intext','filetype','minus'].forEach(op => {
        const el = document.getElementById(`dir-${op}`);
        if (el && el.value.trim()) payload.operators[op] = el.value.trim();
      });
    }
  }

  if (tab === 'files') {
    payload.preset_id = document.getElementById('ff-preset').value;
    const mode = getMode('ff');
    if (mode === 'advanced') {
      const kw = document.getElementById('ff-keywords').value.trim();
      payload.keywords = kw ? kw.split(/\s+/) : [];
      ['intext','inurl','filetype','minus'].forEach(op => {
        const el = document.getElementById(`ff-${op}`);
        if (el && el.value.trim()) payload.operators[op] = el.value.trim();
      });
    }
  }

  try {
    const resp = await fetch('/api/dork', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload)
    });
    const data = await resp.json();
    updatePreview(tab, data.dork);
  } catch (e) {
    console.error('Error calling /api/dork', e);
  }
}

function updatePreview(tab, dork) {
  const idMap = { builder: 'preview-builder', dirs: 'preview-dirs', files: 'preview-files' };
  const googleMap = { builder: 'google-builder', dirs: 'google-dirs', files: 'google-files' };
  const el = document.getElementById(idMap[tab]);
  const gl = document.getElementById(googleMap[tab]);
  if (el) el.textContent = dork;
  if (gl) gl.href = 'https://www.google.com/search?q=' + encodeURIComponent(dork);
}

// ── Presets tab ──────────────────────────────────────────────────────────────
function usePreset(pid, template) {
  document.querySelectorAll('.preset-item').forEach(el => el.classList.remove('selected'));
  const item = document.querySelector(`.preset-item[data-pid="${pid}"]`);
  if (item) item.classList.add('selected');
  const box = document.getElementById('preview-presets');
  if (box) box.textContent = template;
  const gl = document.getElementById('google-presets');
  if (gl) gl.href = 'https://www.google.com/search?q=' + encodeURIComponent(template);
}

// ── Copy to clipboard ────────────────────────────────────────────────────────
function copyDork(tab) {
  const idMap = {
    builder: 'preview-builder',
    dirs:    'preview-dirs',
    files:   'preview-files',
    presets: 'preview-presets'
  };
  const el = document.getElementById(idMap[tab]);
  if (!el) return;
  const text = el.textContent;
  if (!text || text.startsWith('(')) return;
  navigator.clipboard.writeText(text).then(() => {
    const btn = el.closest('.preview-card, .wizard-card')
                  ?.querySelector('.btn-copy');
    if (btn) {
      const orig = btn.innerHTML;
      btn.innerHTML = '&#x2705; Copied!';
      setTimeout(() => { btn.innerHTML = orig; }, 1500);
    }
  });
}
