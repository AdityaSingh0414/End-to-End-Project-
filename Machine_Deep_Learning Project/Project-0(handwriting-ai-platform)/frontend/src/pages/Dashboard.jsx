import React, { useState } from 'react';
import DrawingCanvas from '../components/DrawingCanvas';
import ImageUploader from '../components/ImageUploader';
import PredictionViewer from '../components/PredictionViewer';
import AnalyticsDashboard from '../components/AnalyticsDashboard';
import { apiClient } from '../api/client';

const Dashboard = () => {
  const [activeTab, setActiveTab] = useState('workspace'); // 'workspace' or 'analytics'
  const [mode, setMode] = useState('auto'); // 'auto', 'digits', 'letters'
  const [autocorrect, setAutocorrect] = useState(true);
  const [dilation, setDilation] = useState(1);
  const [splitRatio, setSplitRatio] = useState(1.4);
  const [isProcessing, setIsProcessing] = useState(false);
  const [predictionResult, setPredictionResult] = useState(null);
  const [refreshTrigger, setRefreshTrigger] = useState(0);

  const handlePredict = async (imageBase64, filename) => {
    setIsProcessing(true);
    try {
      const result = await apiClient.predict({
        image: imageBase64,
        mode,
        autocorrect,
        dilation,
        splitRatio,
        filename
      });
      setPredictionResult(result);
      setRefreshTrigger(prev => prev + 1); // Trigger log tables refresh
      return result;
    } catch (error) {
      console.error("Prediction failed:", error);
      alert("Error: " + (error.message || "Could not process prediction. Make sure models are generated and the Flask backend is running."));
    } finally {
      setIsProcessing(false);
    }
  };

  return (
    <div className="dashboard-layout">
      {/* 1. Header Navbar */}
      <header className="navbar">
        <div className="nav-container">
          <div className="logo-group">
            <span className="logo-icon">🔮</span>
            <div>
              <h1 className="nav-title">AURA Recognizer</h1>
              <p className="nav-subtitle font-mono text-[9px] text-slate-500 uppercase tracking-widest">Handwriting AI Platform</p>
            </div>
          </div>
          
          <nav className="nav-tabs">
            <button 
              onClick={() => setActiveTab('workspace')}
              className={`nav-tab-btn ${activeTab === 'workspace' ? 'active' : ''}`}
            >
              Workspace Sandbox
            </button>
            <button 
              onClick={() => setActiveTab('analytics')}
              className={`nav-tab-btn ${activeTab === 'analytics' ? 'active' : ''}`}
            >
              Analytics & Curves
            </button>
          </nav>
        </div>
      </header>

      {/* 2. Main Content Wrapper */}
      <main className="main-content container py-6">
        
        {activeTab === 'workspace' ? (
          <div className="workspace-view grid grid-cols-1 lg:grid-cols-3 gap-6">
            
            {/* COLUMN 1: INTERACTIVE INPUTS (Canvas, Uploader) & SETTINGS */}
            <div className="lg:col-span-1 flex flex-col gap-6">
              
              {/* Pipeline Engine Configuration */}
              <div className="card">
                <div className="card-header border-b border-slate-800 pb-2 mb-4">
                  <h3 className="card-title">Recognition Engine Controls</h3>
                </div>
                
                <div className="flex flex-col gap-4">
                  {/* Mode Selector */}
                  <div className="flex flex-col gap-1.5">
                    <span className="text-xs font-semibold text-slate-400">Classification Mode:</span>
                    <div className="grid grid-cols-3 gap-1 bg-slate-950 p-1 rounded-lg border border-slate-850">
                      {['auto', 'digits', 'letters'].map((m) => (
                        <button
                          key={m}
                          onClick={() => setMode(m)}
                          className={`py-1.5 px-2 text-xs font-medium rounded-md capitalize transition-all ${
                            mode === m 
                              ? 'bg-gradient-to-r from-emerald-600 to-emerald-500 text-white font-semibold' 
                              : 'text-slate-400 hover:text-slate-200'
                          }`}
                        >
                          {m === 'auto' ? 'Auto-Mode' : m}
                        </button>
                      ))}
                    </div>
                  </div>

                  {/* Autocorrect Toggle */}
                  <div className="flex items-center justify-between py-2 border-y border-slate-850">
                    <div className="flex flex-col">
                      <span className="text-xs font-semibold text-slate-300">Spell Auto-Correction</span>
                      <span className="text-[10px] text-slate-500">Search top-5 probabilities</span>
                    </div>
                    <label className="switch-container cursor-pointer relative w-9 h-5">
                      <input 
                        type="checkbox"
                        checked={autocorrect}
                        onChange={(e) => setAutocorrect(e.target.checked)}
                        disabled={mode === 'digits'}
                        className="switch-input hidden"
                      />
                      <span className={`switch-slider absolute inset-0 rounded-full transition-colors ${
                        autocorrect && mode !== 'digits' ? 'bg-emerald-500' : 'bg-slate-800'
                      }`}></span>
                    </label>
                  </div>

                  {/* CV Hyperparameters */}
                  <div className="flex flex-col gap-3">
                    <span className="text-xs font-semibold text-slate-400">OpenCV Preprocessing Parameters:</span>
                    
                    <div className="flex flex-col gap-1">
                      <div className="flex justify-between text-[11px] text-slate-400">
                        <span>Stroke Dilation (Dilation)</span>
                        <span className="font-mono text-slate-200">{dilation} px</span>
                      </div>
                      <input 
                        type="range" 
                        min="0" 
                        max="3" 
                        value={dilation} 
                        onChange={(e) => setDilation(parseInt(e.target.value))}
                        className="slider"
                      />
                      <span className="text-[9px] text-slate-650">Thickness for fragmented strokes (i, j, A, H)</span>
                    </div>

                    <div className="flex flex-col gap-1 mt-1">
                      <div className="flex justify-between text-[11px] text-slate-400">
                        <span>Valley-Split Threshold Ratio</span>
                        <span className="font-mono text-slate-200">{splitRatio.toFixed(1)} w/h</span>
                      </div>
                      <input 
                        type="range" 
                        min="0.8" 
                        max="2.2" 
                        step="0.1"
                        value={splitRatio} 
                        onChange={(e) => setSplitRatio(parseFloat(e.target.value))}
                        className="slider"
                      />
                      <span className="text-[9px] text-slate-650">Width threshold for connected characters split</span>
                    </div>
                  </div>
                </div>
              </div>

              {/* Input Tabs: Canvas vs File Uploader */}
              <DrawingCanvas 
                onPredict={handlePredict} 
                isProcessing={isProcessing} 
              />
              
              <ImageUploader 
                onPredictFile={handlePredict} 
                isProcessing={isProcessing} 
              />
              
            </div>

            {/* COLUMN 2-3: OUTPUT VISUALIZER PANEL */}
            <div className="lg:col-span-2">
              <PredictionViewer 
                predictionData={predictionResult} 
              />
            </div>

          </div>
        ) : (
          <div className="analytics-view">
            <AnalyticsDashboard refreshTrigger={refreshTrigger} />
          </div>
        )}
      </main>

      {/* Footer copyright */}
      <footer className="footer border-t border-slate-900 mt-12 py-6 text-center text-[10px] text-slate-600">
        <div className="container">
          <p>© 2026 AURA Handwriting AI Platform. Powered by TensorFlow & OpenCV. Special Thanks to CodeAlpha.</p>
        </div>
      </footer>
    </div>
  );
};

export default Dashboard;
