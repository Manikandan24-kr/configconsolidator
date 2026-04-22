import React, { useState, useEffect, useRef, useCallback } from 'react';

const API = '/api';

const CATEGORIES = [
  'abstract', 'acronyms', 'capitalization', 'hyphenation', 'numbers',
  'punctuation', 'references', 'spelling', 'statistical_terms',
  'trademarks', 'units', 'figures', 'general_style',
];

const CATEGORY_LABELS = {
  abstract: 'Abstract',
  acronyms: 'Acronyms',
  capitalization: 'Capitalization',
  hyphenation: 'Hyphenation',
  numbers: 'Numbers',
  punctuation: 'Punctuation',
  references: 'References',
  spelling: 'Spelling',
  statistical_terms: 'Statistical Terms',
  trademarks: 'Trademarks',
  units: 'Units',
  figures: 'Figures & Tables',
  general_style: 'General Style',
};

// ── Icons ─────────────────────────────────────────────────────────
const Icons = {
  FileText: () => <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><polyline points="14 2 14 8 20 8"/><line x1="16" y1="13" x2="8" y2="13"/><line x1="16" y1="17" x2="8" y2="17"/><polyline points="10 9 9 9 8 9"/></svg>,
  Upload: () => <svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/><polyline points="17 8 12 3 7 8"/><line x1="12" y1="3" x2="12" y2="15"/></svg>,
  UploadSm: () => <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/><polyline points="17 8 12 3 7 8"/><line x1="12" y1="3" x2="12" y2="15"/></svg>,
  Download: () => <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/><polyline points="7 10 12 15 17 10"/><line x1="12" y1="15" x2="12" y2="3"/></svg>,
  Check: () => <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round"><polyline points="20 6 9 17 4 12"/></svg>,
  X: () => <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round"><line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/></svg>,
  Edit: () => <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7"/><path d="M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z"/></svg>,
  Plus: () => <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round"><line x1="12" y1="5" x2="12" y2="19"/><line x1="5" y1="12" x2="19" y2="12"/></svg>,
  Trash: () => <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><polyline points="3 6 5 6 21 6"/><path d="M19 6l-1 14H6L5 6"/><path d="M10 11v6"/><path d="M14 11v6"/><path d="M9 6V4h6v2"/></svg>,
  AlertTriangle: () => <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z"/><line x1="12" y1="9" x2="12" y2="13"/><line x1="12" y1="17" x2="12.01" y2="17"/></svg>,
  ArrowLeft: () => <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><line x1="19" y1="12" x2="5" y2="12"/><polyline points="12 19 5 12 12 5"/></svg>,
};


// ── Main App ──────────────────────────────────────────────────────
export default function App() {
  return (
    <div className="app-container">
      <div className="top-bar">
        <div className="top-bar-left">
          <div className="logo">KRIYADOCS<span>Config Consolidator</span></div>
        </div>
      </div>
      <div className="main-content">
        <ConsolidatorApp />
      </div>
    </div>
  );
}


// ── Consolidator App (4-view) ─────────────────────────────────────
function ConsolidatorApp() {
  const [view, setView] = useState('sessions');
  const [activeSessionId, setActiveSessionId] = useState(null);

  const goToSession = (sid) => {
    setActiveSessionId(sid);
    setView('review');
  };

  const startNew = () => {
    setActiveSessionId(null);
    setView('upload');
  };

  const goToExtracting = (sid) => {
    setActiveSessionId(sid);
    setView('extracting');
  };

  const goBack = () => {
    setView('sessions');
    setActiveSessionId(null);
  };

  if (view === 'sessions') return <SessionList onNew={startNew} onOpen={goToSession} />;
  if (view === 'upload') return <UploadView onBack={goBack} onStartExtraction={goToExtracting} />;
  if (view === 'extracting') return <ExtractionProgress sessionId={activeSessionId} onDone={goToSession} />;
  if (view === 'review') return <ReviewView sessionId={activeSessionId} onBack={goBack} />;
  return null;
}


// ── Session List ──────────────────────────────────────────────────
function SessionList({ onNew, onOpen }) {
  const [sessions, setSessions] = useState([]);
  const [loading, setLoading] = useState(true);

  const fetchSessions = useCallback(async () => {
    try {
      const res = await fetch(`${API}/sessions`);
      const data = await res.json();
      setSessions(Array.isArray(data) ? data : (data.sessions || []));
    } catch (e) {
      setSessions([]);
    }
    setLoading(false);
  }, []);

  useEffect(() => { fetchSessions(); }, [fetchSessions]);

  const handleDelete = async (e, sid) => {
    e.stopPropagation();
    if (!confirm('Delete this session and all its rules?')) return;
    await fetch(`${API}/sessions/${sid}`, { method: 'DELETE' });
    fetchSessions();
  };

  const statusColor = {
    pending: '#94a3b8',
    uploading: '#f59e0b',
    extracting: '#3b82f6',
    review: '#8b5cf6',
    completed: '#10b981',
  };
  const statusLabel = {
    pending: 'Pending',
    uploading: 'Uploading',
    extracting: 'Extracting…',
    review: 'Ready for Review',
    completed: 'Completed',
  };

  return (
    <div>
      <div className="cc-page-header">
        <div>
          <h1 className="cc-page-title">Sessions</h1>
          <p className="cc-page-subtitle">One session per customer — upload style guides, extract rules, review and export.</p>
        </div>
        <button className="btn btn-primary cc-btn-icon" onClick={onNew}>
          <Icons.Plus /> New Customer
        </button>
      </div>

      {loading ? (
        <div className="cc-loading"><div className="spinner" /></div>
      ) : sessions.length === 0 ? (
        <div className="cc-empty-state">
          <Icons.FileText />
          <h3>No sessions yet</h3>
          <p>Create a new customer session to start extracting rules from style guides.</p>
          <button className="btn btn-primary" onClick={onNew}>Create First Session</button>
        </div>
      ) : (
        <div className="cc-session-grid">
          {sessions.map(s => (
            <div key={s.id} className="cc-session-card" onClick={() => {
              if (s.status === 'extracting') return;
              onOpen(s.id);
            }}>
              <div className="cc-session-card-top">
                <div className="cc-session-name">{s.customer_name}</div>
                <span className="cc-status-dot" style={{ background: statusColor[s.status] || '#94a3b8' }}>
                  {statusLabel[s.status] || s.status}
                </span>
              </div>
              <div className="cc-session-meta">
                {s.total_rules > 0 && (
                  <span>{s.confirmed_rules}/{s.total_rules} rules confirmed</span>
                )}
                {s.total_rules > 0 && (
                  <div className="cc-mini-progress">
                    <div className="cc-mini-progress-fill" style={{ width: `${Math.round((s.confirmed_rules / s.total_rules) * 100)}%` }} />
                  </div>
                )}
                <span className="cc-session-date">{new Date(s.created_at).toLocaleDateString()}</span>
              </div>
              <div className="cc-session-actions">
                {s.status === 'extracting' ? (
                  <span style={{ fontSize: 12, color: '#3b82f6' }}>Processing…</span>
                ) : (
                  <span className="cc-link">Open →</span>
                )}
                <button className="cc-icon-btn cc-danger" onClick={(e) => handleDelete(e, s.id)} title="Delete">
                  <Icons.Trash />
                </button>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}


// ── Upload View ───────────────────────────────────────────────────
function UploadView({ onBack, onStartExtraction }) {
  const [sessionId, setSessionId] = useState(null);
  const [customerName, setCustomerName] = useState('');
  const [files, setFiles] = useState([]);
  const [uploading, setUploading] = useState(false);
  const [uploaded, setUploaded] = useState(false);
  const [error, setError] = useState('');
  const fileInputRef = useRef(null);

  const handleSessionCreated = (sid, cname) => {
    setSessionId(sid);
    setCustomerName(cname);
  };

  const handleFiles = (selected) => {
    const pdfs = Array.from(selected).filter(f => f.name.toLowerCase().endsWith('.pdf'));
    setFiles(prev => {
      const existing = new Set(prev.map(f => f.name));
      return [...prev, ...pdfs.filter(f => !existing.has(f.name))];
    });
  };

  const removeFile = (name) => setFiles(prev => prev.filter(f => f.name !== name));

  const handleUpload = async () => {
    if (!files.length || !sessionId) return;
    setUploading(true);
    setError('');
    try {
      const formData = new FormData();
      files.forEach(f => formData.append('files', f));
      const res = await fetch(`${API}/sessions/${sessionId}/upload`, { method: 'POST', body: formData });
      if (!res.ok) throw new Error((await res.json()).detail || 'Upload failed');
      setUploaded(true);
    } catch (e) {
      setError(e.message);
    }
    setUploading(false);
  };

  const handleStartExtraction = async () => {
    try {
      await fetch(`${API}/sessions/${sessionId}/extract`, { method: 'POST' });
      onStartExtraction(sessionId);
    } catch (e) {
      setError('Failed to start extraction');
    }
  };

  if (!sessionId) {
    return <UploadSessionCreator onCreated={handleSessionCreated} onBack={onBack} />;
  }

  return (
    <div>
      <button className="cc-back-btn" onClick={onBack}><Icons.ArrowLeft /> All Sessions</button>
      <div className="cc-page-header">
        <div>
          <h1 className="cc-page-title">{customerName}</h1>
          <p className="cc-page-subtitle">Upload publisher style guide PDFs to begin extraction.</p>
        </div>
      </div>

      <div className="card">
        <div className="card-body">
          <div
            className="upload-zone"
            onClick={() => fileInputRef.current?.click()}
            onDragOver={e => { e.preventDefault(); e.currentTarget.classList.add('dragover'); }}
            onDragLeave={e => e.currentTarget.classList.remove('dragover')}
            onDrop={e => { e.preventDefault(); e.currentTarget.classList.remove('dragover'); handleFiles(e.dataTransfer.files); }}
          >
            <Icons.Upload />
            <h3>Drop style guide PDFs here or click to browse</h3>
            <p>Multiple PDFs supported. All rules will be extracted and deduplicated.</p>
            <input ref={fileInputRef} type="file" accept=".pdf" multiple style={{ display: 'none' }} onChange={e => handleFiles(e.target.files)} />
          </div>

          {files.length > 0 && (
            <div className="cc-file-list">
              {files.map(f => (
                <div key={f.name} className="cc-file-item">
                  <Icons.FileText />
                  <span className="cc-file-name">{f.name}</span>
                  <span className="cc-file-size">{(f.size / 1024).toFixed(0)} KB</span>
                  <button className="cc-icon-btn cc-danger" onClick={() => removeFile(f.name)}><Icons.X /></button>
                </div>
              ))}
            </div>
          )}

          {error && <div className="cc-error-banner"><Icons.AlertTriangle /> {error}</div>}

          <div className="cc-upload-actions">
            {!uploaded ? (
              <button className="btn btn-primary btn-lg cc-btn-icon" onClick={handleUpload} disabled={uploading || files.length === 0}>
                <Icons.UploadSm /> {uploading ? 'Uploading…' : `Upload ${files.length > 0 ? files.length + ' File' + (files.length > 1 ? 's' : '') : 'Files'}`}
              </button>
            ) : (
              <div className="cc-upload-success">
                <span className="cc-success-msg"><Icons.Check /> {files.length} file{files.length > 1 ? 's' : ''} uploaded</span>
                <button className="btn btn-primary btn-lg" onClick={handleStartExtraction}>
                  Start Extraction →
                </button>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}


// ── Session creator used by UploadView ────────────────────────────
function UploadSessionCreator({ onCreated, onBack }) {
  const [name, setName] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const inputRef = useRef(null);
  useEffect(() => { inputRef.current?.focus(); }, []);

  const handleCreate = async () => {
    if (!name.trim()) { setError('Customer name is required'); return; }
    setLoading(true);
    try {
      const res = await fetch(`${API}/sessions`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ customer_name: name.trim() }),
      });
      const data = await res.json();
      onCreated(data.id, name.trim());
    } catch (e) {
      setError('Failed to create session');
      setLoading(false);
    }
  };

  return (
    <div>
      <button className="cc-back-btn" onClick={onBack}><Icons.ArrowLeft /> All Sessions</button>
      <div className="cc-modal-overlay" onClick={onBack}>
        <div className="cc-modal" onClick={e => e.stopPropagation()}>
          <div className="cc-modal-header">
            <h2>New Customer Session</h2>
            <button className="cc-icon-btn" onClick={onBack}><Icons.X /></button>
          </div>
          <div className="cc-modal-body">
            <label className="cc-label">Customer / Publisher Name</label>
            <input
              ref={inputRef}
              className="cc-input"
              placeholder="e.g. AAAS / Science"
              value={name}
              onChange={e => { setName(e.target.value); setError(''); }}
              onKeyDown={e => e.key === 'Enter' && handleCreate()}
            />
            {error && <div className="cc-field-error">{error}</div>}
          </div>
          <div className="cc-modal-footer">
            <button className="btn" onClick={onBack}>Cancel</button>
            <button className="btn btn-primary" onClick={handleCreate} disabled={loading}>
              {loading ? 'Creating…' : 'Create & Upload'}
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}


// ── Extraction Progress ───────────────────────────────────────────
function ExtractionProgress({ sessionId, onDone }) {
  const [status, setStatus] = useState({ progress: 0, message: 'Starting…', status: 'extracting' });
  const pollRef = useRef(null);

  useEffect(() => {
    if (!sessionId) return;
    pollRef.current = setInterval(async () => {
      try {
        const res = await fetch(`${API}/sessions/${sessionId}/status`);
        const data = await res.json();
        setStatus(data);
        if (data.status === 'review' || data.status === 'completed') {
          clearInterval(pollRef.current);
          onDone(sessionId);
        }
      } catch (e) { /* keep polling */ }
    }, 2000);
    return () => clearInterval(pollRef.current);
  }, [sessionId, onDone]);

  return (
    <div className="processing-screen">
      <div className="spinner" />
      <h2>Extracting Rules</h2>
      <p style={{ color: 'var(--gray-500)', marginBottom: 24 }}>{status.message}</p>
      <div style={{ maxWidth: 440, margin: '0 auto' }}>
        <div className="progress-bar-container">
          <div className="progress-bar-fill" style={{ width: `${status.progress}%` }} />
        </div>
        <p style={{ fontSize: 13, color: 'var(--gray-400)', marginTop: 8 }}>{status.progress}% complete</p>
      </div>
    </div>
  );
}


// ── Review View ───────────────────────────────────────────────────
function ReviewView({ sessionId, onBack }) {
  const [session, setSession] = useState(null);
  const [rules, setRules] = useState([]);
  const [activeCategory, setActiveCategory] = useState(CATEGORIES[0]);
  const [activeFilter, setActiveFilter] = useState('all');
  const [editingRule, setEditingRule] = useState(null);
  const [addingRule, setAddingRule] = useState(false);
  const [loading, setLoading] = useState(true);
  const [exportMenuOpen, setExportMenuOpen] = useState(false);
  const [addFilesOpen, setAddFilesOpen] = useState(false);
  const [extracting, setExtracting] = useState(false);
  const [extractProgress, setExtractProgress] = useState({ progress: 0, message: '' });
  const exportMenuRef = useRef(null);
  const pollRef = useRef(null);

  const fetchData = useCallback(async () => {
    try {
      const [sessRes, rulesRes] = await Promise.all([
        fetch(`${API}/sessions/${sessionId}`),
        fetch(`${API}/sessions/${sessionId}/rules`),
      ]);
      const sessData = await sessRes.json();
      const rulesData = await rulesRes.json();
      setSession(sessData);
      setRules(rulesData.rules || []);
    } catch (e) { /* ignore */ }
    setLoading(false);
  }, [sessionId]);

  useEffect(() => { fetchData(); }, [fetchData]);

  const startPolling = useCallback(() => {
    setExtracting(true);
    pollRef.current = setInterval(async () => {
      try {
        const res = await fetch(`${API}/sessions/${sessionId}/status`);
        const data = await res.json();
        setExtractProgress({ progress: data.progress, message: data.message });
        if (data.status === 'review' || data.status === 'completed') {
          clearInterval(pollRef.current);
          setExtracting(false);
          fetchData();
        }
      } catch (e) { /* keep polling */ }
    }, 2000);
  }, [sessionId, fetchData]);

  useEffect(() => () => clearInterval(pollRef.current), []);

  useEffect(() => {
    const handler = (e) => {
      if (exportMenuRef.current && !exportMenuRef.current.contains(e.target)) {
        setExportMenuOpen(false);
      }
    };
    document.addEventListener('mousedown', handler);
    return () => document.removeEventListener('mousedown', handler);
  }, []);

  const categoryMap = useCallback(() => {
    const map = {};
    CATEGORIES.forEach(c => { map[c] = []; });
    rules.forEach(r => {
      if (map[r.category] !== undefined) map[r.category].push(r);
    });
    return map;
  }, [rules])();

  const counts = CATEGORIES.reduce((acc, c) => {
    const cat = categoryMap[c] || [];
    acc[c] = {
      total: cat.length,
      confirmed: cat.filter(r => r.status === 'confirmed').length,
      pending: cat.filter(r => r.status === 'pending').length,
    };
    return acc;
  }, {});

  const visibleRules = (categoryMap[activeCategory] || []).filter(r => {
    if (activeFilter === 'all') return true;
    return r.status === activeFilter;
  });

  const handleStatusChange = async (ruleId, newStatus) => {
    setRules(prev => prev.map(r => r.id === ruleId ? { ...r, status: newStatus } : r));
    await fetch(`${API}/rules/${ruleId}`, {
      method: 'PATCH',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ status: newStatus }),
    });
    fetchData();
  };

  const handleBulkAction = async (action) => {
    const targetIds = visibleRules.map(r => r.id);
    if (!targetIds.length) return;
    const newStatus = action === 'confirm' ? 'confirmed' : 'excluded';
    setRules(prev => prev.map(r => targetIds.includes(r.id) ? { ...r, status: newStatus } : r));
    await fetch(`${API}/sessions/${sessionId}/rules/bulk`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ rule_ids: targetIds, action }),
    });
    fetchData();
  };

  const handleSaveEdit = async (ruleId, updates) => {
    await fetch(`${API}/rules/${ruleId}`, {
      method: 'PATCH',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(updates),
    });
    setEditingRule(null);
    fetchData();
  };

  const handleAddRule = async (ruleData) => {
    await fetch(`${API}/sessions/${sessionId}/rules`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ ...ruleData, category: activeCategory }),
    });
    setAddingRule(false);
    fetchData();
  };

  const handleDeleteRule = async (ruleId) => {
    await fetch(`${API}/rules/${ruleId}`, { method: 'DELETE' });
    fetchData();
  };

  const handleExport = async (format) => {
    setExportMenuOpen(false);
    const a = document.createElement('a');
    a.href = `${API}/sessions/${sessionId}/export/${format}`;
    a.download = `${session?.customer_name || 'rules'}_config.${format === 'excel' ? 'xlsx' : 'json'}`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
  };

  if (loading) return <div className="cc-loading"><div className="spinner" /></div>;

  const totalConfirmed = rules.filter(r => r.status === 'confirmed').length;
  const totalRules = rules.length;
  const overallPct = totalRules > 0 ? Math.round((totalConfirmed / totalRules) * 100) : 0;

  return (
    <div className="cc-review-layout">
      <div className="cc-review-header">
        <div className="cc-review-header-left">
          <button className="cc-back-btn" style={{ margin: 0 }} onClick={onBack}><Icons.ArrowLeft /> Sessions</button>
          <div>
            <h1 className="cc-review-title">{session?.customer_name || 'Session'}</h1>
            <div className="cc-review-stats">
              <span>{totalConfirmed} confirmed</span>
              <span>·</span>
              <span>{rules.filter(r => r.status === 'pending').length} pending</span>
              <span>·</span>
              <span>{rules.filter(r => r.status === 'excluded').length} excluded</span>
              <span>·</span>
              <span>{totalRules} total</span>
            </div>
          </div>
        </div>
        <div className="cc-review-header-right">
          <div className="cc-overall-progress">
            <span className="cc-progress-label">{overallPct}% reviewed</span>
            <div className="cc-progress-track">
              <div className="cc-progress-fill" style={{ width: `${overallPct}%` }} />
            </div>
          </div>
          <button className="btn cc-btn-icon" onClick={() => setAddFilesOpen(true)} disabled={extracting}>
            <Icons.UploadSm /> Add Style Guide
          </button>
          <div className="cc-export-wrap" ref={exportMenuRef}>
            <button className="btn cc-btn-icon" onClick={() => setExportMenuOpen(!exportMenuOpen)} disabled={extracting}>
              <Icons.Download /> Export
            </button>
            {exportMenuOpen && (
              <div className="cc-export-menu">
                <button onClick={() => handleExport('excel')}>Download Excel (.xlsx)</button>
                <button onClick={() => handleExport('json')}>Download JSON</button>
              </div>
            )}
          </div>
        </div>
      </div>

      {extracting && (
        <div className="cc-inline-progress">
          <div className="spinner" style={{ width: 20, height: 20, margin: 0, flexShrink: 0 }} />
          <div className="cc-inline-progress-bar">
            <div className="cc-inline-progress-fill" style={{ width: `${extractProgress.progress}%` }} />
          </div>
          <span className="cc-inline-progress-msg">{extractProgress.message || 'Extracting…'} {extractProgress.progress}%</span>
        </div>
      )}

      <div className="cc-review-body">
        <div className="cc-category-sidebar">
          <div className="cc-sidebar-title">Categories</div>
          {CATEGORIES.map(cat => {
            const c = counts[cat];
            const allDone = c.total > 0 && c.pending === 0;
            const isActive = cat === activeCategory;
            return (
              <div
                key={cat}
                className={`cc-cat-item ${isActive ? 'active' : ''} ${allDone ? 'done' : ''}`}
                onClick={() => { setActiveCategory(cat); setActiveFilter('all'); }}
              >
                <span className="cc-cat-label">{CATEGORY_LABELS[cat]}</span>
                <span className={`cc-cat-badge ${allDone ? 'done' : c.confirmed > 0 ? 'partial' : ''}`}>
                  {c.confirmed}/{c.total}
                </span>
              </div>
            );
          })}
        </div>

        <div className="cc-rule-panel">
          <div className="cc-rule-panel-header">
            <div className="cc-rule-panel-title">
              <h2>{CATEGORY_LABELS[activeCategory]}</h2>
              <span className="cc-rule-count">{(categoryMap[activeCategory] || []).length} rules</span>
            </div>
            <div className="cc-rule-panel-actions">
              <div className="cc-filter-tabs">
                {[
                  { key: 'all', label: `All (${(categoryMap[activeCategory] || []).length})` },
                  { key: 'pending', label: `Pending (${(categoryMap[activeCategory] || []).filter(r => r.status === 'pending').length})` },
                  { key: 'confirmed', label: `Confirmed (${(categoryMap[activeCategory] || []).filter(r => r.status === 'confirmed').length})` },
                  { key: 'excluded', label: `Excluded (${(categoryMap[activeCategory] || []).filter(r => r.status === 'excluded').length})` },
                ].map(f => (
                  <button key={f.key} className={`cc-filter-tab ${activeFilter === f.key ? 'active' : ''}`} onClick={() => setActiveFilter(f.key)}>
                    {f.label}
                  </button>
                ))}
              </div>
              <div className="cc-bulk-actions">
                <button className="btn cc-btn-sm cc-btn-confirm cc-btn-icon" onClick={() => handleBulkAction('confirm')}>
                  <Icons.Check /> Confirm All
                </button>
                <button className="btn cc-btn-sm cc-btn-exclude cc-btn-icon" onClick={() => handleBulkAction('exclude')}>
                  <Icons.X /> Exclude All
                </button>
                <button className="btn cc-btn-sm cc-btn-icon" onClick={() => setAddingRule(true)}>
                  <Icons.Plus /> Add Rule
                </button>
              </div>
            </div>
          </div>

          <div className="cc-rule-list">
            {visibleRules.length === 0 ? (
              <div className="cc-empty-rules">
                <p>No {activeFilter !== 'all' ? activeFilter : ''} rules in this category.</p>
                {activeFilter === 'all' && (
                  <button className="btn btn-primary cc-btn-icon" onClick={() => setAddingRule(true)}>
                    <Icons.Plus /> Add Custom Rule
                  </button>
                )}
              </div>
            ) : (
              visibleRules.map(rule => (
                <RuleRow
                  key={rule.id}
                  rule={rule}
                  onConfirm={() => handleStatusChange(rule.id, 'confirmed')}
                  onExclude={() => handleStatusChange(rule.id, 'excluded')}
                  onRestore={() => handleStatusChange(rule.id, 'pending')}
                  onEdit={() => setEditingRule(rule)}
                  onDelete={rule.is_custom ? () => handleDeleteRule(rule.id) : null}
                />
              ))
            )}
          </div>
        </div>
      </div>

      {(editingRule || addingRule) && (
        <EditRulePanel
          rule={editingRule}
          category={activeCategory}
          onSave={editingRule ? (updates) => handleSaveEdit(editingRule.id, updates) : handleAddRule}
          onClose={() => { setEditingRule(null); setAddingRule(false); }}
        />
      )}

      {addFilesOpen && (
        <AddFilesModal
          sessionId={sessionId}
          onClose={() => setAddFilesOpen(false)}
          onStarted={() => { setAddFilesOpen(false); startPolling(); }}
        />
      )}
    </div>
  );
}


// ── Add Files Modal ───────────────────────────────────────────────
function AddFilesModal({ sessionId, onClose, onStarted }) {
  const [files, setFiles] = useState([]);
  const [uploading, setUploading] = useState(false);
  const [error, setError] = useState('');
  const fileInputRef = useRef(null);

  const handleFiles = (selected) => {
    const pdfs = Array.from(selected).filter(f => f.name.toLowerCase().endsWith('.pdf'));
    setFiles(prev => {
      const existing = new Set(prev.map(f => f.name));
      return [...prev, ...pdfs.filter(f => !existing.has(f.name))];
    });
  };

  const handleUploadAndExtract = async () => {
    if (!files.length) return;
    setUploading(true);
    setError('');
    try {
      const formData = new FormData();
      files.forEach(f => formData.append('files', f));
      const res = await fetch(`${API}/sessions/${sessionId}/add-files`, {
        method: 'POST',
        body: formData,
      });
      const data = await res.json();
      if (!res.ok) throw new Error(data.detail || 'Upload failed');
      if (data.files_uploaded === 0) {
        setError(`All selected files already exist in this session: ${data.skipped_duplicates.join(', ')}`);
        setUploading(false);
        return;
      }
      if (data.skipped_duplicates?.length > 0) {
        // Some uploaded, some skipped — proceed but note it
        console.info('Skipped duplicates:', data.skipped_duplicates);
      }
      onStarted();
    } catch (e) {
      setError(e.message);
      setUploading(false);
    }
  };

  return (
    <div className="cc-edit-overlay" onClick={onClose}>
      <div className="cc-edit-panel" style={{ width: 520 }} onClick={e => e.stopPropagation()}>
        <div className="cc-edit-header">
          <h3>Add Style Guide</h3>
          <button className="cc-icon-btn" onClick={onClose}><Icons.X /></button>
        </div>
        <div className="cc-edit-body">
          <p style={{ fontSize: 13, color: 'var(--gray-500)', marginBottom: 16 }}>
            Upload additional PDFs. New rules will be extracted and merged with the existing ruleset — duplicates removed automatically.
          </p>
          <div
            className="upload-zone"
            style={{ padding: 32 }}
            onClick={() => fileInputRef.current?.click()}
            onDragOver={e => { e.preventDefault(); e.currentTarget.classList.add('dragover'); }}
            onDragLeave={e => e.currentTarget.classList.remove('dragover')}
            onDrop={e => { e.preventDefault(); e.currentTarget.classList.remove('dragover'); handleFiles(e.dataTransfer.files); }}
          >
            <Icons.Upload />
            <h3 style={{ fontSize: 14 }}>Drop PDFs here or click to browse</h3>
            <input ref={fileInputRef} type="file" accept=".pdf" multiple style={{ display: 'none' }} onChange={e => handleFiles(e.target.files)} />
          </div>
          {files.length > 0 && (
            <div className="cc-file-list" style={{ marginTop: 12 }}>
              {files.map(f => (
                <div key={f.name} className="cc-file-item">
                  <Icons.FileText />
                  <span className="cc-file-name">{f.name}</span>
                  <span className="cc-file-size">{(f.size / 1024).toFixed(0)} KB</span>
                  <button className="cc-icon-btn cc-danger" onClick={() => setFiles(prev => prev.filter(p => p.name !== f.name))}><Icons.X /></button>
                </div>
              ))}
            </div>
          )}
          {error && <div className="cc-error-banner" style={{ marginTop: 12 }}><Icons.AlertTriangle /> {error}</div>}
        </div>
        <div className="cc-edit-footer">
          <button className="btn" onClick={onClose}>Cancel</button>
          <button className="btn btn-primary cc-btn-icon" onClick={handleUploadAndExtract} disabled={uploading || files.length === 0}>
            <Icons.UploadSm /> {uploading ? 'Uploading…' : `Upload & Extract${files.length > 0 ? ` (${files.length})` : ''}`}
          </button>
        </div>
      </div>
    </div>
  );
}


// ── Rule Row ──────────────────────────────────────────────────────
function RuleRow({ rule, onConfirm, onExclude, onRestore, onEdit, onDelete }) {
  const isConfirmed = rule.status === 'confirmed';
  const isExcluded = rule.status === 'excluded';

  return (
    <div className={`cc-rule-row ${rule.status}`}>
      <div className="cc-rule-body">
        <div className="cc-rule-text">{rule.rule}</div>
        <div className="cc-rule-meta">
          {rule.is_custom && <span className="cc-badge cc-badge-custom">Custom</span>}
          {rule.source_document && <span className="cc-badge cc-badge-source">{rule.source_document}</span>}
          {rule.source_section && <span className="cc-badge cc-badge-section">{rule.source_section}</span>}
          {rule.remarks && <span className="cc-rule-remarks">Note: {rule.remarks}</span>}
        </div>
      </div>
      <div className="cc-rule-actions">
        {!isConfirmed && !isExcluded && (
          <>
            <button className="cc-action-btn cc-confirm" onClick={onConfirm} title="Confirm"><Icons.Check /></button>
            <button className="cc-action-btn cc-exclude" onClick={onExclude} title="Exclude"><Icons.X /></button>
          </>
        )}
        {(isConfirmed || isExcluded) && (
          <button className="cc-action-btn cc-restore" onClick={onRestore} title="Reset to pending">↩</button>
        )}
        <button className="cc-action-btn cc-edit" onClick={onEdit} title="Edit"><Icons.Edit /></button>
        {onDelete && (
          <button className="cc-action-btn cc-delete" onClick={onDelete} title="Delete"><Icons.Trash /></button>
        )}
        <span className={`cc-status-pill ${rule.status}`}>{rule.status}</span>
      </div>
    </div>
  );
}


// ── Edit / Add Rule Panel ─────────────────────────────────────────
function EditRulePanel({ rule, category, onSave, onClose }) {
  const [text, setText] = useState(rule?.rule || '');
  const [remarks, setRemarks] = useState(rule?.remarks || '');
  const [saving, setSaving] = useState(false);
  const textRef = useRef(null);

  useEffect(() => { textRef.current?.focus(); }, []);

  const handleSave = async () => {
    if (!text.trim()) return;
    setSaving(true);
    await onSave({ rule: text.trim(), remarks: remarks.trim() || null });
    setSaving(false);
  };

  return (
    <div className="cc-edit-overlay" onClick={onClose}>
      <div className="cc-edit-panel" onClick={e => e.stopPropagation()}>
        <div className="cc-edit-header">
          <h3>{rule ? 'Edit Rule' : `Add Rule — ${CATEGORY_LABELS[category]}`}</h3>
          <button className="cc-icon-btn" onClick={onClose}><Icons.X /></button>
        </div>
        <div className="cc-edit-body">
          <label className="cc-label">Rule</label>
          <textarea
            ref={textRef}
            className="cc-textarea"
            placeholder="Write the rule as a clear imperative sentence…"
            value={text}
            onChange={e => setText(e.target.value)}
            rows={4}
          />
          <label className="cc-label" style={{ marginTop: 16 }}>Remarks (optional)</label>
          <input
            className="cc-input"
            placeholder="Any nuance or exception not captured in the rule…"
            value={remarks}
            onChange={e => setRemarks(e.target.value)}
          />
        </div>
        <div className="cc-edit-footer">
          <button className="btn" onClick={onClose}>Cancel</button>
          <button className="btn btn-primary" onClick={handleSave} disabled={saving || !text.trim()}>
            {saving ? 'Saving…' : rule ? 'Save Changes' : 'Add Rule'}
          </button>
        </div>
      </div>
    </div>
  );
}
