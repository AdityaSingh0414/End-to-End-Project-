import React, { useState, useEffect } from 'react';

const PredictionViewer = ({ predictionData }) => {
  const [selectedChar, setSelectedChar] = useState(null);

  // Auto-select the first non-space character when new data arrives
  useEffect(() => {
    if (predictionData && predictionData.characters) {
      const firstChar = predictionData.characters.find(c => !c.is_space);
      setSelectedChar(firstChar || null);
    } else {
      setSelectedChar(null);
    }
  }, [predictionData]);

  if (!predictionData) {
    return (
      <div className="viewer-container card flex flex-col justify-center items-center text-center p-12 min-h-[400px]">
        <div className="text-slate-600 text-6xl mb-4 font-thin">✍️</div>
        <h3 className="text-lg font-semibold text-slate-400">No Prediction Results Yet</h3>
        <p className="text-sm text-slate-500 max-w-xs mt-1">
          Draw on the canvas or upload images above to view real-time binarization and character classifications.
        </p>
      </div>
    );
  }

  const { raw_text, corrected_text, avg_confidence, mode, annotated_image, characters } = predictionData;

  return (
    <div className="viewer-container card grid grid-cols-1 md:grid-cols-2 gap-6">
      
      {/* LEFT: Image Visualization & Metrics */}
      <div className="flex flex-col gap-4">
        <div className="card-header border-b border-slate-800 pb-2">
          <h3 className="card-title">Computer Vision Output</h3>
          <span className="badge badge-success text-[10px]">
            {mode === 'auto' ? 'Auto-Mode' : mode === 'digits' ? 'Digits-Only' : 'Letters-Only'}
          </span>
        </div>
        
        <div className="annotated-image-wrapper rounded-lg border border-slate-800 overflow-hidden bg-slate-950 flex items-center justify-center p-2 min-h-[220px]">
          {annotated_image ? (
            <img 
              src={annotated_image} 
              alt="OCR Segmented" 
              className="max-h-[300px] object-contain rounded"
            />
          ) : (
            <span className="text-slate-600 text-sm">Visualizer offline</span>
          )}
        </div>
        
        {/* Results Block */}
        <div className="grid grid-cols-1 gap-3 mt-1">
          <div className="p-3 rounded bg-slate-900/80 border border-slate-800 flex flex-col">
            <span className="text-[10px] uppercase font-semibold tracking-wider text-slate-500 mb-1">
              Final Recognized Text (Autocorrected)
            </span>
            <span className="text-2xl font-bold text-emerald-400 tracking-wide font-mono">
              {corrected_text || '—'}
            </span>
          </div>

          <div className="grid grid-cols-2 gap-3">
            <div className="p-3 rounded bg-slate-900/50 border border-slate-800/80 flex flex-col">
              <span className="text-[10px] uppercase font-semibold tracking-wider text-slate-500 mb-0.5">
                Raw Model Predictions
              </span>
              <span className="text-base font-semibold text-slate-300 font-mono">
                {raw_text || '—'}
              </span>
            </div>
            
            <div className="p-3 rounded bg-slate-900/50 border border-slate-800/80 flex flex-col">
              <span className="text-[10px] uppercase font-semibold tracking-wider text-slate-500 mb-0.5">
                Average Confidence
              </span>
              <span className="text-base font-semibold text-emerald-400 font-mono">
                {(avg_confidence * 100).toFixed(1)}%
              </span>
            </div>
          </div>
        </div>
      </div>

      {/* RIGHT: Top-5 Probabilities & Bounding Box Coordinates */}
      <div className="flex flex-col gap-4 border-t md:border-t-0 md:border-l border-slate-850 pt-4 md:pt-0 md:pl-6">
        <div className="card-header border-b border-slate-800 pb-2">
          <h3 className="card-title">Character Probability Matrix</h3>
        </div>

        {/* Character Selection Grid */}
        <div className="character-grid-wrapper">
          <span className="text-xs text-slate-400 block mb-2 font-medium">Select a character to view probability spreads:</span>
          <div className="flex flex-wrap gap-1.5 max-h-[120px] overflow-y-auto p-1 bg-slate-950 rounded border border-slate-900">
            {characters.map((node, index) => {
              if (node.is_space) {
                return (
                  <div 
                    key={`space-${index}`}
                    className="w-8 h-8 rounded border border-dashed border-slate-700/50 bg-slate-900/30 flex items-center justify-center text-[10px] text-slate-600 select-none"
                    title="Detected space boundary"
                  >
                    ␣
                  </div>
                );
              }
              
              const top1 = node.predictions?.[0]?.[0] || '?';
              const top1Conf = node.predictions?.[0]?.[1] || 0;
              const isSelected = selectedChar && selectedChar.id === node.id;
              
              return (
                <button
                  key={node.id}
                  onClick={() => setSelectedChar(node)}
                  className={`w-8 h-8 rounded border text-xs font-mono font-bold flex flex-col items-center justify-center transition-all ${
                    isSelected 
                      ? 'bg-emerald-500 border-emerald-400 text-slate-950 shadow-md shadow-emerald-500/10' 
                      : 'bg-slate-900 border-slate-800 text-slate-300 hover:border-slate-700 hover:bg-slate-850'
                  }`}
                >
                  <span>{top1}</span>
                </button>
              );
            })}
          </div>
        </div>

        {/* Top-5 Charts */}
        <div className="top5-chart flex-1 flex flex-col justify-center">
          {selectedChar ? (
            <div className="flex flex-col h-full justify-between">
              <div>
                <div className="flex justify-between items-baseline mb-2 bg-slate-900/50 p-2 rounded border border-slate-850">
                  <span className="text-xs text-slate-400">
                    Char Index: <strong className="text-slate-200">#{selectedChar.id}</strong>
                  </span>
                  <span className="text-xs text-slate-400 font-mono">
                    Bounds: <strong className="text-slate-200">({selectedChar.x}, {selectedChar.y}, {selectedChar.w}x{selectedChar.h})</strong>
                  </span>
                </div>
                
                <div className="flex flex-col gap-2 mt-3">
                  {selectedChar.predictions?.slice(0, 5).map(([char, conf], idx) => {
                    const pct = (conf * 100).toFixed(1);
                    return (
                      <div key={idx} className="flex items-center text-xs gap-3">
                        <div className="w-4 text-center font-bold font-mono text-slate-200">{char}</div>
                        <div className="flex-1 h-4 bg-slate-900 rounded-full overflow-hidden border border-slate-800 relative">
                          <div 
                            className="h-full bg-gradient-to-r from-emerald-600 to-emerald-400 rounded-full transition-all duration-500"
                            style={{ width: `${pct}%` }}
                          />
                        </div>
                        <div className="w-10 text-right font-mono text-[10px] text-slate-400 font-semibold">{pct}%</div>
                      </div>
                    );
                  })}
                </div>
              </div>
              
              <div className="text-[10px] text-slate-500 mt-4 text-right">
                Inference loaded from {mode === 'digits' ? 'CNN (MNIST)' : 'CRNN (EMNIST)'}
              </div>
            </div>
          ) : (
            <div className="text-center p-6 bg-slate-950 rounded border border-slate-900 text-slate-500 text-xs">
              No character selected.
            </div>
          )}
        </div>

      </div>

    </div>
  );
};

export default PredictionViewer;
