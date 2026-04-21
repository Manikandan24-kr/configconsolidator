import React, { useState, useEffect, useRef, useCallback } from 'react';
import * as XLSX from 'xlsx';

const API = '/api';

// ── Icons (inline SVGs to avoid dependency issues) ────────────────
const Icons = {
  FileText: () => <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><polyline points="14 2 14 8 20 8"/><line x1="16" y1="13" x2="8" y2="13"/><line x1="16" y1="17" x2="8" y2="17"/><polyline points="10 9 9 9 8 9"/></svg>,
  Shield: () => <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/></svg>,
  MessageCircle: () => <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M21 11.5a8.38 8.38 0 0 1-.9 3.8 8.5 8.5 0 0 1-7.6 4.7 8.38 8.38 0 0 1-3.8-.9L3 21l1.9-5.7a8.38 8.38 0 0 1-.9-3.8 8.5 8.5 0 0 1 4.7-7.6 8.38 8.38 0 0 1 3.8-.9h.5a8.48 8.48 0 0 1 8 8v.5z"/></svg>,
  Upload: () => <svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/><polyline points="17 8 12 3 7 8"/><line x1="12" y1="3" x2="12" y2="15"/></svg>,
  Check: () => <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><polyline points="20 6 9 17 4 12"/></svg>,
  AlertTriangle: () => <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z"/><line x1="12" y1="9" x2="12" y2="13"/><line x1="12" y1="17" x2="12.01" y2="17"/></svg>,
  ChevronRight: () => <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><polyline points="9 18 15 12 9 6"/></svg>,
  Send: () => <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><line x1="22" y1="2" x2="11" y2="13"/><polygon points="22 2 15 22 11 13 2 9 22 2"/></svg>,
  BarChart: () => <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><line x1="12" y1="20" x2="12" y2="10"/><line x1="18" y1="20" x2="18" y2="4"/><line x1="6" y1="20" x2="6" y2="16"/></svg>,
  Home: () => <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M3 9l9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"/><polyline points="9 22 9 12 15 12 15 22"/></svg>,
};


// ── Main App ──────────────────────────────────────────────────────
export default function App() {
  const [activeTab, setActiveTab] = useState('home');
  const [sessionId, setSessionId] = useState(null);

  return (
    <div className="app-container">
      <div className="top-bar">
        <div className="top-bar-left">
          <div className="logo">KRIYADOCS<span>AI Onboarding Platform</span></div>
        </div>
        <div className="tab-bar">
          <div className={`tab ${activeTab === 'home' ? 'active' : ''}`} onClick={() => setActiveTab('home')}>
            <Icons.Home /> Overview
          </div>
          <div className={`tab ${activeTab === 'consolidator' ? 'active' : ''}`} onClick={() => setActiveTab('consolidator')}>
            <Icons.FileText /> Configuration Consolidator
          </div>
          <div className={`tab ${activeTab === 'qc' ? 'active' : ''}`} onClick={() => setActiveTab('qc')}>
            <Icons.Shield /> Quality Checker
          </div>
          <div className={`tab ${activeTab === 'knowledge' ? 'active' : ''}`} onClick={() => setActiveTab('knowledge')}>
            <Icons.MessageCircle /> Knowledge Agent
          </div>
        </div>
      </div>
      <div className="main-content">
        {activeTab === 'home' && <HomePage onNavigate={setActiveTab} />}
        {activeTab === 'consolidator' && <ConsolidatorPage sessionId={sessionId} setSessionId={setSessionId} />}
        {activeTab === 'qc' && <QualityCheckerPage />}
        {activeTab === 'knowledge' && <KnowledgeAgentPage sessionId={sessionId} />}
      </div>
    </div>
  );
}


// ── Home Page ─────────────────────────────────────────────────────
function HomePage({ onNavigate }) {
  return (
    <div>
      <div className="hero">
        <h1>Reimagine <span className="gradient">Publisher Engagement</span></h1>
        <p>
          Convert the onboarding process into a strategic consulting opportunity.
          Turn ambiguity into alignment — before it costs you.
        </p>
      </div>
      <div className="deliverables-grid">
        <div className="deliverable-card" onClick={() => onNavigate('consolidator')}>
          <div className="deliverable-icon" style={{ background: '#ede9fe', color: '#7c3aed' }}>
            <Icons.FileText />
          </div>
          <div className="deliverable-subtitle">Sign-Off Document</div>
          <h3>Codified Rule Set</h3>
          <p>Upload style guides and get a structured, signed-off document that defines exactly what KriyaDocs will and won't do. New requests fall outside it, creating a clear upsell mechanism.</p>
        </div>
        <div className="deliverable-card" onClick={() => onNavigate('qc')}>
          <div className="deliverable-icon" style={{ background: '#fef3c7', color: '#d97706' }}>
            <Icons.Shield />
          </div>
          <div className="deliverable-subtitle">Audit Tool</div>
          <h3>Compliance Detector</h3>
          <p>Analyzes manuscripts and surfaces where actual practice diverges from stated policy — giving publishers an honest audit of their own work at scale.</p>
        </div>
        <div className="deliverable-card" onClick={() => onNavigate('knowledge')}>
          <div className="deliverable-icon" style={{ background: '#dbeafe', color: '#2563eb' }}>
            <Icons.MessageCircle />
          </div>
          <div className="deliverable-subtitle">AI Tool</div>
          <h3>RAG Knowledge Agent</h3>
          <p>An AI agent trained on the publisher's own rules. Anyone on the team can ask "How should we handle X?" and get an instant, consistent answer.</p>
        </div>
        <div className="deliverable-card" onClick={() => onNavigate('consolidator')}>
          <div className="deliverable-icon" style={{ background: '#dcfce7', color: '#16a34a' }}>
            <Icons.BarChart />
          </div>
          <div className="deliverable-subtitle">Strategy Report</div>
          <h3>Risk & Opportunity Assessment</h3>
          <p>Identifies gaps, conflicts, missed opportunities, and risk areas in the publisher's current style guidelines — turning onboarding into strategic advisory.</p>
        </div>
      </div>
    </div>
  );
}


// ── Consolidator Page ─────────────────────────────────────────────
function ConsolidatorPage({ sessionId, setSessionId }) {
  const [files, setFiles] = useState([]);
  const [uploading, setUploading] = useState(false);
  const [processing, setProcessing] = useState(false);
  const [progress, setProgress] = useState(0);
  const [progressMsg, setProgressMsg] = useState('');
  const [results, setResults] = useState(null);
  const [activeFilter, setActiveFilter] = useState('all');
  const [expandedCategories, setExpandedCategories] = useState({});
  const fileInputRef = useRef(null);
  const pollRef = useRef(null);

  const handleFiles = (selectedFiles) => {
    const pdfs = Array.from(selectedFiles).filter(f => f.name.toLowerCase().endsWith('.pdf'));
    setFiles(pdfs);
  };

  const handleUploadAndProcess = async () => {
    if (files.length === 0) return;
    setUploading(true);

    try {
      const formData = new FormData();
      files.forEach(f => formData.append('files', f));

      const uploadRes = await fetch(`${API}/consolidator/upload`, { method: 'POST', body: formData });
      const uploadData = await uploadRes.json();
      const sid = uploadData.session_id;
      setSessionId(sid);

      // Start processing
      await fetch(`${API}/consolidator/process/${sid}`, { method: 'POST' });
      setUploading(false);
      setProcessing(true);

      // Poll for status
      pollRef.current = setInterval(async () => {
        const statusRes = await fetch(`${API}/consolidator/status/${sid}`);
        const status = await statusRes.json();
        setProgress(status.progress);
        setProgressMsg(status.message);

        if (status.status === 'completed') {
          clearInterval(pollRef.current);
          const resultsRes = await fetch(`${API}/consolidator/results/${sid}`);
          const resultsData = await resultsRes.json();
          setResults(resultsData);
          setProcessing(false);
        } else if (status.status === 'failed') {
          clearInterval(pollRef.current);
          setProcessing(false);
          alert('Processing failed: ' + status.message);
        }
      }, 2000);
    } catch (err) {
      setUploading(false);
      setProcessing(false);
      alert('Error: ' + err.message);
    }
  };

  const handleLoadDemo = async (publisher) => {
    setUploading(true);
    const endpoint = publisher === 'bmj' ? 'load-bmj-guides' : 'load-science-guides';
    try {
      const res = await fetch(`${API}/demo/${endpoint}`, { method: 'POST' });
      const data = await res.json();
      const sid = data.session_id;
      setSessionId(sid);
      setUploading(false);
      setProcessing(true);

      pollRef.current = setInterval(async () => {
        const statusRes = await fetch(`${API}/consolidator/status/${sid}`);
        const status = await statusRes.json();
        setProgress(status.progress);
        setProgressMsg(status.message);

        if (status.status === 'completed') {
          clearInterval(pollRef.current);
          const resultsRes = await fetch(`${API}/consolidator/results/${sid}`);
          const resultsData = await resultsRes.json();
          setResults(resultsData);
          setProcessing(false);
        } else if (status.status === 'failed') {
          clearInterval(pollRef.current);
          setProcessing(false);
          alert('Processing failed: ' + status.message);
        }
      }, 2000);
    } catch (err) {
      setUploading(false);
      alert('Error: ' + err.message);
    }
  };

  useEffect(() => { return () => { if (pollRef.current) clearInterval(pollRef.current); }; }, []);

  const toggleCategory = (cat) => {
    setExpandedCategories(prev => ({ ...prev, [cat]: !prev[cat] }));
  };

  // Upload / Processing view
  if (!results && !processing) {
    return (
      <div>
        <div style={{ marginBottom: 24 }}>
          <h1 style={{ fontSize: 24, fontWeight: 700, marginBottom: 4 }}>Configuration Consolidator</h1>
          <p style={{ color: 'var(--gray-500)' }}>Upload publisher style guides to extract, structure, and validate editorial rules.</p>
        </div>

        <div className="card">
          <div className="card-body">
            <div
              className="upload-zone"
              onClick={() => fileInputRef.current?.click()}
              onDragOver={(e) => { e.preventDefault(); e.currentTarget.classList.add('dragover'); }}
              onDragLeave={(e) => e.currentTarget.classList.remove('dragover')}
              onDrop={(e) => { e.preventDefault(); e.currentTarget.classList.remove('dragover'); handleFiles(e.dataTransfer.files); }}
            >
              <Icons.Upload />
              <h3>Drop style guide PDFs here or click to browse</h3>
              <p>Supports multiple PDF files. We'll extract and analyze all rules.</p>
              <input
                ref={fileInputRef}
                type="file"
                accept=".pdf"
                multiple
                style={{ display: 'none' }}
                onChange={(e) => handleFiles(e.target.files)}
              />
            </div>

            {files.length > 0 && (
              <div style={{ marginTop: 16 }}>
                <p style={{ fontWeight: 500, marginBottom: 8 }}>{files.length} file(s) selected:</p>
                {files.map((f, i) => (
                  <div key={i} style={{ fontSize: 13, color: 'var(--gray-600)', padding: '2px 0' }}>
                    <Icons.FileText /> {f.name} ({(f.size / 1024).toFixed(0)} KB)
                  </div>
                ))}
                <button className="btn btn-primary btn-lg" style={{ marginTop: 16 }} onClick={handleUploadAndProcess} disabled={uploading}>
                  {uploading ? 'Uploading...' : 'Upload & Process'}
                </button>
              </div>
            )}

            <div style={{ marginTop: 24, textAlign: 'center', borderTop: '1px solid var(--gray-100)', paddingTop: 24 }}>
              <p style={{ color: 'var(--gray-400)', fontSize: 13, marginBottom: 12 }}>Or try a demo with pre-loaded style guides</p>
              <div style={{ display: 'flex', gap: 12, justifyContent: 'center' }}>
                <button className="btn btn-lg" onClick={() => handleLoadDemo('aaas')} disabled={uploading}
                  style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                  <span style={{ fontSize: 18 }}>S</span> Load Science/AAAS
                </button>
                <button className="btn btn-lg" onClick={() => handleLoadDemo('bmj')} disabled={uploading}
                  style={{ display: 'flex', alignItems: 'center', gap: 8, background: 'var(--brand)', color: '#fff' }}>
                  <span style={{ fontSize: 18 }}>B</span> Load BMJ
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
    );
  }

  if (processing) {
    return (
      <div className="processing-screen">
        <div className="spinner" />
        <h2>Processing Style Guides</h2>
        <p>{progressMsg}</p>
        <div style={{ maxWidth: 400, margin: '20px auto' }}>
          <div className="progress-bar-container">
            <div className="progress-bar-fill" style={{ width: `${progress}%` }} />
          </div>
          <p style={{ fontSize: 13, color: 'var(--gray-400)', marginTop: 8 }}>{progress}% complete</p>
        </div>
      </div>
    );
  }

  // Results view
  const stats = results.stats;
  const rules = results.rules_by_category;
  const discrepancies = results.discrepancies || [];

  const filteredDiscrepancies = activeFilter === 'all'
    ? discrepancies
    : discrepancies.filter(d => d.type === activeFilter);

  const handleDownloadExcel = () => {
    const wb = XLSX.utils.book_new();

    // ── Sheet 1: Extracted Rules ──
    const rulesRows = [];
    Object.entries(rules).forEach(([category, subcats]) => {
      Object.entries(subcats).forEach(([subcategory, ruleList]) => {
        ruleList.forEach((r) => {
          rulesRows.push({
            'Rule ID': r.rule_id,
            'Category': category,
            'Subcategory': subcategory,
            'Rule': r.rule,
            'Correct Examples': (r.examples?.correct || []).join(' | '),
            'Incorrect Examples': (r.examples?.incorrect || []).join(' | '),
            'Exceptions': (r.exceptions || []).join(' | '),
            'Check Method': r.automatable === 'deterministic' ? 'Deterministic (regex/dictionary)'
              : r.automatable === 'ai_high' ? 'AI — High Confidence'
              : r.automatable === 'ai_moderate' ? 'AI — Moderate'
              : 'Manual Review Needed',
            'Automation Notes': r.automation_notes || '',
            'Source Document': r.source?.document || '',
            'Source Section': r.source?.section || '',
          });
        });
      });
    });
    const wsRules = XLSX.utils.json_to_sheet(rulesRows);
    // Set column widths
    wsRules['!cols'] = [
      { wch: 22 }, { wch: 14 }, { wch: 20 }, { wch: 60 },
      { wch: 40 }, { wch: 40 }, { wch: 30 }, { wch: 28 },
      { wch: 30 }, { wch: 25 }, { wch: 20 },
    ];
    XLSX.utils.book_append_sheet(wb, wsRules, 'Extracted Rules');

    // ── Sheet 2: Discrepancies & Gaps ──
    const discRows = discrepancies.map((d, idx) => ({
      '#': idx + 1,
      'Type': (d.type || '').charAt(0).toUpperCase() + (d.type || '').slice(1),
      'Severity': (d.severity || '').charAt(0).toUpperCase() + (d.severity || '').slice(1),
      'Title': d.title,
      'Description': d.description,
      'Affected Rules': (d.affected_rules || []).join(', '),
      'Recommendation': d.recommendation || '',
    }));
    const wsDisc = XLSX.utils.json_to_sheet(discRows);
    wsDisc['!cols'] = [
      { wch: 5 }, { wch: 12 }, { wch: 10 }, { wch: 40 },
      { wch: 70 }, { wch: 35 }, { wch: 60 },
    ];
    XLSX.utils.book_append_sheet(wb, wsDisc, 'Discrepancies & Gaps');

    // ── Sheet 3: Summary ──
    const summaryRows = [
      { 'Metric': 'Total Rules Extracted', 'Value': stats.total_rules },
      { 'Metric': 'Discrepancies Found', 'Value': stats.total_discrepancies },
      { 'Metric': 'Auto-Checkable (Deterministic)', 'Value': stats.by_automation?.deterministic || 0 },
      { 'Metric': 'AI — High Confidence', 'Value': stats.by_automation?.ai_high || 0 },
      { 'Metric': 'AI — Moderate', 'Value': stats.by_automation?.ai_moderate || 0 },
      { 'Metric': 'Needs Human Review', 'Value': stats.by_automation?.manual || 0 },
      { 'Metric': 'Documents Processed', 'Value': stats.documents_processed },
      { 'Metric': '', 'Value': '' },
      { 'Metric': 'Discrepancy Breakdown', 'Value': '' },
      { 'Metric': 'Conflicts', 'Value': discrepancies.filter(d => d.type === 'conflict').length },
      { 'Metric': 'Ambiguities', 'Value': discrepancies.filter(d => d.type === 'ambiguity').length },
      { 'Metric': 'Gaps', 'Value': discrepancies.filter(d => d.type === 'gap').length },
      { 'Metric': 'Overlaps', 'Value': discrepancies.filter(d => d.type === 'overlap').length },
    ];
    const wsSummary = XLSX.utils.json_to_sheet(summaryRows);
    wsSummary['!cols'] = [{ wch: 32 }, { wch: 12 }];
    XLSX.utils.book_append_sheet(wb, wsSummary, 'Summary');

    XLSX.writeFile(wb, 'StyleGuide_Analysis_Report.xlsx');
  };

  return (
    <div>
      <div style={{ marginBottom: 24, display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <div>
          <h1 style={{ fontSize: 24, fontWeight: 700, marginBottom: 4 }}>Publisher Style Guide Analysis</h1>
          <p style={{ color: 'var(--gray-500)' }}>
            Processed {stats.documents_processed} documents — {stats.total_rules} rules extracted
          </p>
        </div>
        <div style={{ display: 'flex', gap: 8 }}>
          <button className="btn" onClick={handleDownloadExcel}
            style={{ background: 'var(--success)', display: 'flex', alignItems: 'center', gap: 6 }}>
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/><polyline points="7 10 12 15 17 10"/><line x1="12" y1="15" x2="12" y2="3"/></svg>
            Download Excel
          </button>
          <button className="btn" onClick={() => { setResults(null); setFiles([]); setProgress(0); }}>
            Analyze New Documents
          </button>
        </div>
      </div>

      {/* Stats */}
      <div className="stats-grid">
        <div className="stat-card">
          <div className="stat-value" style={{ color: 'var(--brand)' }}>{stats.total_rules}</div>
          <div className="stat-label">Rules Extracted</div>
        </div>
        <div className="stat-card">
          <div className="stat-value" style={{ color: 'var(--danger)' }}>{stats.total_discrepancies}</div>
          <div className="stat-label">Discrepancies Found</div>
        </div>
        <div className="stat-card">
          <div className="stat-value" style={{ color: 'var(--success)' }}>{stats.by_automation?.deterministic || 0}</div>
          <div className="stat-label">Auto-Checkable Rules</div>
        </div>
        <div className="stat-card">
          <div className="stat-value" style={{ color: 'var(--gray-400)' }}>{stats.by_automation?.manual || 0}</div>
          <div className="stat-label">Needs Human Review</div>
        </div>
      </div>

      <div className="two-col">
        {/* Rules panel */}
        <div className="card">
          <div className="card-header">
            <h2>Extracted Rules ({stats.total_rules})</h2>
          </div>
          <div className="card-body">
            <div className="legend">
              <div className="legend-item"><div className="legend-dot deterministic" /> Deterministic (regex/dictionary)</div>
              <div className="legend-item"><div className="legend-dot ai_high" /> AI — High confidence</div>
              <div className="legend-item"><div className="legend-dot ai_moderate" /> AI — Moderate</div>
              <div className="legend-item"><div className="legend-dot manual" /> Manual review needed</div>
            </div>

            {Object.entries(rules).map(([category, subcats]) => {
              const ruleCount = Object.values(subcats).reduce((a, b) => a + b.length, 0);
              const isOpen = expandedCategories[category] !== false; // default open
              return (
                <div key={category} className="category-section">
                  <div className="category-header section-toggle" onClick={() => toggleCategory(category)}>
                    <span className={`chevron ${isOpen ? 'open' : ''}`}><Icons.ChevronRight /></span>
                    <h3>{category}</h3>
                    <span className="category-count">{ruleCount}</span>
                  </div>
                  {isOpen && Object.entries(subcats).map(([sub, rulesList]) => (
                    <div key={sub} className="subcategory-section">
                      <h4>{sub} ({rulesList.length})</h4>
                      {rulesList.slice(0, 5).map((r, i) => (
                        <div key={i} className={`rule-item ${r.automatable}`}>
                          <div><strong>{r.rule_id}</strong></div>
                          <div>{r.rule}</div>
                          {r.examples && (r.examples.correct?.length > 0 || r.examples.incorrect?.length > 0) && (
                            <div className="rule-examples">
                              {r.examples.correct?.slice(0, 2).map((ex, j) => (
                                <div key={j} className="correct">Correct: {ex}</div>
                              ))}
                              {r.examples.incorrect?.slice(0, 2).map((ex, j) => (
                                <div key={j} className="incorrect">Incorrect: {ex}</div>
                              ))}
                            </div>
                          )}
                          <div className="rule-source">
                            Source: {r.source?.document} {r.source?.section && `— ${r.source.section}`}
                          </div>
                        </div>
                      ))}
                      {rulesList.length > 5 && (
                        <div style={{ fontSize: 12, color: 'var(--gray-400)', paddingLeft: 12 }}>
                          + {rulesList.length - 5} more rules in this subcategory
                        </div>
                      )}
                    </div>
                  ))}
                </div>
              );
            })}
          </div>
        </div>

        {/* Discrepancies panel */}
        <div className="card">
          <div className="card-header">
            <h2>Discrepancies & Gaps ({discrepancies.length})</h2>
          </div>
          <div className="card-body">
            <div className="filter-tabs">
              {['all', 'conflict', 'ambiguity', 'gap', 'overlap'].map(f => (
                <button
                  key={f}
                  className={`filter-tab ${activeFilter === f ? 'active' : ''}`}
                  onClick={() => setActiveFilter(f)}
                >
                  {f === 'all' ? `All (${discrepancies.length})` : `${f} (${discrepancies.filter(d => d.type === f).length})`}
                </button>
              ))}
            </div>

            {filteredDiscrepancies.length === 0 ? (
              <p style={{ color: 'var(--gray-400)', textAlign: 'center', padding: 40 }}>
                No discrepancies in this category.
              </p>
            ) : (
              filteredDiscrepancies.map((d, i) => (
                <div key={i} className={`discrepancy-item ${d.severity}`}>
                  <div className="discrepancy-header">
                    <span className="discrepancy-title">{d.title}</span>
                    <div style={{ display: 'flex', gap: 6 }}>
                      <span className={`discrepancy-type type-${d.type}`}>{d.type}</span>
                      <span className={`issue-badge badge-${d.severity === 'high' ? 'error' : d.severity === 'medium' ? 'warning' : 'info'}`}>{d.severity}</span>
                    </div>
                  </div>
                  <p style={{ fontSize: 13, color: 'var(--gray-600)', marginBottom: 8 }}>{d.description}</p>
                  {d.recommendation && (
                    <div style={{ fontSize: 12, color: 'var(--brand)', fontWeight: 500, background: 'var(--brand-light)', padding: '6px 10px', borderRadius: 6 }}>
                      Recommendation: {d.recommendation}
                    </div>
                  )}
                  {d.affected_rules?.length > 0 && (
                    <div style={{ fontSize: 11, color: 'var(--gray-400)', marginTop: 6 }}>
                      Affected rules: {d.affected_rules.join(', ')}
                    </div>
                  )}
                </div>
              ))
            )}
          </div>
        </div>
      </div>
    </div>
  );
}


// ── Quality Checker Page ──────────────────────────────────────────
function QualityCheckerPage() {
  const [text, setText] = useState('');
  const [docName, setDocName] = useState('');
  const [loading, setLoading] = useState(false);
  const [report, setReport] = useState(null);
  const [issueFilter, setIssueFilter] = useState('all');

  const loadSample = async () => {
    try {
      const res = await fetch(`${API}/qc/sample`);
      const data = await res.json();
      setText(data.text);
      setDocName(data.name);
    } catch (err) {
      alert('Failed to load sample: ' + err.message);
    }
  };

  const runCheck = async () => {
    if (!text.trim()) return;
    setLoading(true);
    setReport(null);
    try {
      const res = await fetch(`${API}/qc/check`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ text, document_name: docName || 'Uploaded Document', use_ai: true }),
      });
      const data = await res.json();
      setReport(data);
    } catch (err) {
      alert('QC check failed: ' + err.message);
    }
    setLoading(false);
  };

  const getFilteredIssues = () => {
    if (!report) return [];
    if (issueFilter === 'all') return report.issues;
    return report.issues.filter(i => i.confidence === issueFilter);
  };

  const getConfidenceColor = (pct) => {
    if (pct >= 90) return 'var(--danger)';
    if (pct >= 75) return 'var(--warning)';
    if (pct >= 50) return 'var(--info)';
    return 'var(--gray-400)';
  };

  if (!report) {
    return (
      <div>
        <div style={{ marginBottom: 24 }}>
          <h1 style={{ fontSize: 24, fontWeight: 700, marginBottom: 4 }}>Quality Checker</h1>
          <p style={{ color: 'var(--gray-500)' }}>Paste or upload a manuscript to check it against Science style rules with confidence scoring.</p>
        </div>

        <div className="card">
          <div className="card-body">
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 12 }}>
              <label style={{ fontWeight: 500, fontSize: 14 }}>Manuscript Text</label>
              <button className="btn" onClick={loadSample}>Load Sample Manuscript</button>
            </div>
            <textarea
              value={text}
              onChange={(e) => setText(e.target.value)}
              placeholder="Paste your manuscript text here..."
              style={{ minHeight: 400 }}
            />
            <div style={{ marginTop: 16, display: 'flex', gap: 12, alignItems: 'center' }}>
              <button className="btn btn-primary btn-lg" onClick={runCheck} disabled={loading || !text.trim()}>
                {loading ? 'Analyzing...' : 'Run Quality Check'}
              </button>
              {loading && <div className="spinner" style={{ width: 24, height: 24, margin: 0 }} />}
            </div>
          </div>
        </div>
      </div>
    );
  }

  // Report view
  const summary = report.summary;
  const filteredIssues = getFilteredIssues();

  return (
    <div>
      <div style={{ marginBottom: 24, display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <div>
          <h1 style={{ fontSize: 24, fontWeight: 700, marginBottom: 4 }}>Quality Check Report</h1>
          <p style={{ color: 'var(--gray-500)' }}>{report.document_name}</p>
        </div>
        <button className="btn" onClick={() => setReport(null)}>Check Another Document</button>
      </div>

      <div className="stats-grid">
        <div className="stat-card" style={{ borderLeft: '4px solid var(--danger)' }}>
          <div className="stat-value" style={{ color: 'var(--danger)' }}>{summary.definitive_issues}</div>
          <div className="stat-label">Definitive Issues — Fix These</div>
        </div>
        <div className="stat-card" style={{ borderLeft: '4px solid var(--warning)' }}>
          <div className="stat-value" style={{ color: 'var(--warning)' }}>{summary.high_confidence_issues}</div>
          <div className="stat-label">High Confidence — Likely Fix</div>
        </div>
        <div className="stat-card" style={{ borderLeft: '4px solid var(--info)' }}>
          <div className="stat-value" style={{ color: 'var(--info)' }}>{summary.moderate_confidence_issues}</div>
          <div className="stat-label">Moderate — Human Review</div>
        </div>
        <div className="stat-card" style={{ borderLeft: '4px solid var(--gray-300)' }}>
          <div className="stat-value" style={{ color: 'var(--gray-400)' }}>{summary.unchecked_rules}</div>
          <div className="stat-label">Rules Not Checkable by AI</div>
        </div>
      </div>

      <div className="two-col">
        <div className="card">
          <div className="card-header">
            <h2>Issues Found ({report.issues.length})</h2>
          </div>
          <div className="card-body">
            <div className="filter-tabs">
              {[
                { key: 'all', label: `All (${report.issues.length})` },
                { key: 'definitive', label: `Definitive (${summary.definitive_issues})` },
                { key: 'high', label: `High (${summary.high_confidence_issues})` },
                { key: 'moderate', label: `Moderate (${summary.moderate_confidence_issues})` },
                { key: 'low', label: `Low (${summary.low_confidence_issues})` },
              ].map(f => (
                <button
                  key={f.key}
                  className={`filter-tab ${issueFilter === f.key ? 'active' : ''}`}
                  onClick={() => setIssueFilter(f.key)}
                >
                  {f.label}
                </button>
              ))}
            </div>

            <div className="issue-list">
              {filteredIssues.map((issue, i) => (
                <div key={i} className="issue-item">
                  <span className={`issue-badge badge-${issue.severity}`}>{issue.severity}</span>
                  <div className="issue-content">
                    <div className="issue-text">
                      Found: <code style={{ background: 'var(--danger-light)', padding: '1px 4px', borderRadius: 3, fontSize: 12 }}>{issue.found_text}</code>
                    </div>
                    <div className="issue-suggestion">{issue.suggestion}</div>
                    <div className="issue-location">{issue.location} — Rule: {issue.rule_id}</div>
                  </div>
                  <div className="issue-confidence">
                    <div className="confidence-pct">{issue.confidence_pct}%</div>
                    <div className="confidence-bar">
                      <div
                        className="confidence-fill"
                        style={{
                          width: `${issue.confidence_pct}%`,
                          background: getConfidenceColor(issue.confidence_pct),
                        }}
                      />
                    </div>
                  </div>
                </div>
              ))}
              {filteredIssues.length === 0 && (
                <p style={{ textAlign: 'center', color: 'var(--gray-400)', padding: 40 }}>
                  No issues in this confidence level.
                </p>
              )}
            </div>
          </div>
        </div>

        <div className="card">
          <div className="card-header">
            <h2>Rules We Could NOT Check ({report.unchecked_rules.length})</h2>
          </div>
          <div className="card-body">
            <p style={{ fontSize: 13, color: 'var(--gray-500)', marginBottom: 16 }}>
              These rules require human judgment or external verification.
              A human editor must review these areas manually.
            </p>
            <div className="unchecked-list">
              {report.unchecked_rules.map((r, i) => (
                <div key={i} className="unchecked-item">
                  <div className="unchecked-icon" />
                  <div>
                    <div style={{ fontWeight: 500 }}>{r.rule}</div>
                    <div className="unchecked-reason">{r.reason}</div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}


// ── Knowledge Agent Page ──────────────────────────────────────────
function KnowledgeAgentPage({ sessionId }) {
  const [messages, setMessages] = useState([
    { role: 'assistant', content: 'I\'m your style guide knowledge agent. Ask me anything about the publisher\'s editorial rules, and I\'ll give you an instant, consistent answer based on the codified ruleset.\n\nTry asking:\n- "How should we handle acronyms in the abstract?"\n- "What is the reference format for journal articles?"\n- "When should we use active vs. passive voice?"' }
  ]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const messagesEndRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(scrollToBottom, [messages]);

  const sendMessage = async () => {
    if (!input.trim() || loading) return;
    const question = input.trim();
    setInput('');
    setMessages(prev => [...prev, { role: 'user', content: question }]);
    setLoading(true);

    try {
      const res = await fetch(`${API}/knowledge/ask`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ question, session_id: sessionId || 'default' }),
      });
      const data = await res.json();
      setMessages(prev => [...prev, {
        role: 'assistant',
        content: data.answer,
        sources: data.sources,
      }]);
    } catch (err) {
      setMessages(prev => [...prev, {
        role: 'assistant',
        content: 'Sorry, I encountered an error. Please make sure the backend is running and style guides have been processed via the Consolidator.',
      }]);
    }
    setLoading(false);
  };

  return (
    <div>
      <div style={{ marginBottom: 24 }}>
        <h1 style={{ fontSize: 24, fontWeight: 700, marginBottom: 4 }}>Knowledge Agent</h1>
        <p style={{ color: 'var(--gray-500)' }}>
          Ask questions about the publisher's style rules.
          {sessionId ? ` (Using rules from session: ${sessionId})` : ' Process style guides first for best results.'}
        </p>
      </div>

      <div className="card">
        <div className="chat-container">
          <div className="chat-messages">
            {messages.map((msg, i) => (
              <div key={i} className={`chat-message ${msg.role}`}>
                <div style={{ whiteSpace: 'pre-wrap' }}>{msg.content}</div>
                {msg.sources?.length > 0 && (
                  <div style={{ marginTop: 8, fontSize: 11, opacity: 0.8 }}>
                    Sources: {msg.sources.map(s => s.rule_id).join(', ')}
                  </div>
                )}
              </div>
            ))}
            {loading && (
              <div className="chat-message assistant">
                <div className="spinner" style={{ width: 20, height: 20, margin: 0 }} />
              </div>
            )}
            <div ref={messagesEndRef} />
          </div>
          <div className="chat-input-area">
            <input
              type="text"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={(e) => e.key === 'Enter' && sendMessage()}
              placeholder="Ask about style rules..."
              disabled={loading}
            />
            <button className="btn btn-primary" onClick={sendMessage} disabled={loading || !input.trim()}>
              <Icons.Send />
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
