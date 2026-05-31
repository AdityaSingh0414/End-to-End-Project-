import React, { useState, useEffect } from 'react';
import SimpleLineChart from '../charts/SimpleLineChart';
import { apiClient } from '../api/client';

const AnalyticsDashboard = ({ refreshTrigger }) => {
  const [logs, setLogs] = useState([]);
  const [curves, setCurves] = useState(null);
  const [loading, setLoading] = useState(true);
  const [filterMode, setFilterMode] = useState('all');
  const [searchTerm, setSearchTerm] = useState('');

  const fetchAnalytics = async () => {
    try {
      setLoading(true);
      const data = await apiClient.getAnalytics();
      setLogs(data.prediction_history || []);
      setCurves(data.training_curves);
    } catch (error) {
      console.error("Failed to load analytics:", error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchAnalytics();
  }, [refreshTrigger]);

  const handleClearLogs = async () => {
    if (window.confirm("Are you sure you want to delete all prediction logs and reset the CSV dataset?")) {
      try {
        await apiClient.clearLogs();
        setLogs([]);
      } catch (error) {
        alert("Failed to clear logs");
      }
    }
  };

  // Filter logs based on search term and mode dropdown
  const filteredLogs = logs.filter(log => {
    const matchesMode = filterMode === 'all' || log.mode === filterMode;
    const matchesSearch = 
      searchTerm === '' || 
      log.filename.toLowerCase().includes(searchTerm.toLowerCase()) ||
      log.corrected_text.toLowerCase().includes(searchTerm.toLowerCase()) ||
      log.raw_text.toLowerCase().includes(searchTerm.toLowerCase());
    return matchesMode && matchesSearch;
  });

  return (
    <div className="analytics-container grid grid-cols-1 gap-6">
      
      {/* 1. MODEL TRAINING PERFORMANCE SECTION */}
      <div className="card">
        <div className="card-header border-b border-slate-800 pb-2 mb-4">
          <h3 className="card-title">Model Performance & Loss Curves</h3>
          <span className="text-xs text-slate-500 font-mono">TensorFlow Engine Logs</span>
        </div>

        {curves ? (
          <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
            {/* CNN Digits Model */}
            <div className="p-4 rounded-lg bg-slate-900/40 border border-slate-850 flex flex-col gap-4">
              <div className="flex justify-between items-center mb-1">
                <span className="text-xs font-bold text-slate-300">MNIST Digit Model (CNN)</span>
                <span className="text-[10px] text-emerald-400 font-mono bg-emerald-500/10 px-1.5 py-0.5 rounded">Accuracy ~98.5%</span>
              </div>
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                <SimpleLineChart 
                  data={curves.digit_model.accuracy}
                  valData={curves.digit_model.val_accuracy}
                  labels={curves.digit_model.epochs.map(e => `Ep ${e}`)}
                  title="Accuracy"
                  yLabel="Score"
                  strokeColor="#10b981"
                  valStrokeColor="#3b82f6"
                  height={130}
                />
                <SimpleLineChart 
                  data={curves.digit_model.loss}
                  valData={curves.digit_model.val_loss}
                  labels={curves.digit_model.epochs.map(e => `Ep ${e}`)}
                  title="Loss (Entropy)"
                  yLabel="Error"
                  strokeColor="#ef4444"
                  valStrokeColor="#f59e0b"
                  height={130}
                />
              </div>
            </div>

            {/* CRNN Letters Model */}
            <div className="p-4 rounded-lg bg-slate-900/40 border border-slate-850 flex flex-col gap-4">
              <div className="flex justify-between items-center mb-1">
                <span className="text-xs font-bold text-slate-300">EMNIST Letters Model (CRNN)</span>
                <span className="text-[10px] text-emerald-400 font-mono bg-emerald-500/10 px-1.5 py-0.5 rounded">Accuracy ~97.8%</span>
              </div>
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                <SimpleLineChart 
                  data={curves.letter_model.accuracy}
                  valData={curves.letter_model.val_accuracy}
                  labels={curves.letter_model.epochs.map(e => `Ep ${e}`)}
                  title="Accuracy"
                  yLabel="Score"
                  strokeColor="#10b981"
                  valStrokeColor="#3b82f6"
                  height={130}
                />
                <SimpleLineChart 
                  data={curves.letter_model.loss}
                  valData={curves.letter_model.val_loss}
                  labels={curves.letter_model.epochs.map(e => `Ep ${e}`)}
                  title="Loss (Entropy)"
                  yLabel="Error"
                  strokeColor="#ef4444"
                  valStrokeColor="#f59e0b"
                  height={130}
                />
              </div>
            </div>
          </div>
        ) : (
          <div className="text-center py-6 text-slate-500 text-xs">Training profiles unavailable.</div>
        )}
      </div>

      {/* 2. INFERENCE RUNS HISTORY LOGS TABLE */}
      <div className="card">
        <div className="card-header flex flex-wrap gap-4 items-center justify-between border-b border-slate-800 pb-3 mb-4">
          <div>
            <h3 className="card-title">Inference Execution Records</h3>
            <p className="text-[11px] text-slate-500 mt-0.5">Confidence intervals and correction modes</p>
          </div>
          
          <div className="flex gap-2">
            <a 
              href={apiClient.exportCSVUrl} 
              download
              className="btn btn-primary text-xs py-1.5 px-3 flex items-center gap-1.5"
            >
              <svg className="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M12 10v6m0 0l-3-3m3 3l3-3m2 8H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
              </svg>
              Export CSV Dataset
            </a>
            <button 
              onClick={handleClearLogs}
              className="btn btn-danger text-xs py-1.5 px-3"
            >
              Reset History
            </button>
          </div>
        </div>

        {/* Filters */}
        <div className="flex flex-col sm:flex-row gap-3 mb-4">
          <input
            type="text"
            placeholder="Search log items (filename, text output)..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="text-input flex-1 text-xs py-2"
          />
          <select
            value={filterMode}
            onChange={(e) => setFilterMode(e.target.value)}
            className="select-input text-xs py-2 min-w-[140px]"
          >
            <option value="all">All Modes</option>
            <option value="auto">Auto-Mode</option>
            <option value="digits">Digits-Only</option>
            <option value="letters">Letters-Only</option>
          </select>
        </div>

        {/* Table list */}
        {loading ? (
          <div className="text-center py-10 text-xs text-slate-500">Syncing analytics records...</div>
        ) : filteredLogs.length === 0 ? (
          <div className="text-center py-10 text-xs text-slate-500 border border-dashed border-slate-800 rounded bg-slate-950/20">
            No inference logs matched your criteria.
          </div>
        ) : (
          <div className="overflow-x-auto border border-slate-850 rounded-lg">
            <table className="logs-table w-full border-collapse text-left text-xs text-slate-300">
              <thead className="bg-slate-900/80 text-slate-400 font-semibold border-b border-slate-800 uppercase tracking-wider text-[10px]">
                <tr>
                  <th className="p-3 font-medium">Timestamp</th>
                  <th className="p-3 font-medium">Filename</th>
                  <th className="p-3 font-medium">Classification</th>
                  <th className="p-3 font-medium">Raw OCR</th>
                  <th className="p-3 font-medium">Spelling Corrected</th>
                  <th className="p-3 font-medium text-right">Avg Conf.</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-850">
                {filteredLogs.map((log, index) => {
                  const dateStr = new Date(log.timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit' }) + 
                                  ' ' + new Date(log.timestamp).toLocaleDateString([], { month: 'short', day: 'numeric' });
                  return (
                    <tr key={index} className="hover:bg-slate-900/30 transition-colors">
                      <td className="p-3 font-mono text-[10px] text-slate-500">{dateStr}</td>
                      <td className="p-3 font-medium text-slate-350 max-w-[120px] truncate" title={log.filename}>{log.filename}</td>
                      <td className="p-3">
                        <span className={`inline-block px-1.5 py-0.5 rounded-[3px] text-[9px] font-bold ${
                          log.mode === 'auto' ? 'bg-indigo-500/10 text-indigo-400 border border-indigo-500/10' :
                          log.mode === 'digits' ? 'bg-amber-500/10 text-amber-400 border border-amber-500/10' :
                          'bg-sky-500/10 text-sky-400 border border-sky-500/10'
                        }`}>
                          {log.mode}
                        </span>
                      </td>
                      <td className="p-3 font-mono font-bold text-slate-450">{log.raw_text || '—'}</td>
                      <td className="p-3 font-mono font-bold text-emerald-400">{log.corrected_text || '—'}</td>
                      <td className="p-3 font-mono text-right text-slate-350">{(log.avg_confidence * 100).toFixed(1)}%</td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        )}
      </div>

    </div>
  );
};

export default AnalyticsDashboard;
