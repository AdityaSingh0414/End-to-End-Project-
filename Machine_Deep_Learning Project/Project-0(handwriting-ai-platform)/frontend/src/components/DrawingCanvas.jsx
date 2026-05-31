import React, { useRef, useState, useEffect } from 'react';

const DrawingCanvas = ({ onPredict, isProcessing }) => {
  const canvasRef = useRef(null);
  const [isDrawing, setIsDrawing] = useState(false);
  const [brushSize, setBrushSize] = useState(10);
  const [autoPredict, setAutoPredict] = useState(true);
  const [history, setHistory] = useState([]);
  const [historyStep, setHistoryStep] = useState(-1);
  const autoPredictTimeoutRef = useRef(null);

  // Initialize Canvas
  useEffect(() => {
    const canvas = canvasRef.current;
    if (canvas) {
      const ctx = canvas.getContext('2d');
      // Set canvas resolution
      canvas.width = canvas.parentElement.clientWidth || 500;
      canvas.height = 350;
      
      // Clear canvas with black background
      ctx.fillStyle = '#0f172a'; // Tailwind slate-900 background
      ctx.fillRect(0, 0, canvas.width, canvas.height);
      
      // Save initial state
      const initialState = canvas.toDataURL();
      setHistory([initialState]);
      setHistoryStep(0);
    }
  }, []);

  // Handle Window Resize
  useEffect(() => {
    const handleResize = () => {
      const canvas = canvasRef.current;
      if (canvas) {
        // Save current contents
        const tempImage = new Image();
        tempImage.src = canvas.toDataURL();
        
        const ctx = canvas.getContext('2d');
        const oldW = canvas.width;
        const oldH = canvas.height;
        const newW = canvas.parentElement.clientWidth || 500;
        
        canvas.width = newW;
        
        tempImage.onload = () => {
          ctx.fillStyle = '#0f172a';
          ctx.fillRect(0, 0, canvas.width, canvas.height);
          // Draw old canvas contents centered
          ctx.drawImage(tempImage, (newW - oldW) / 2, 0);
        };
      }
    };
    
    window.addEventListener('resize', handleResize);
    return () => window.removeEventListener('resize', handleResize);
  }, []);

  const getCoordinates = (e) => {
    const canvas = canvasRef.current;
    if (!canvas) return null;
    
    const rect = canvas.getBoundingClientRect();
    
    // Check if touch or mouse
    if (e.touches && e.touches.length > 0) {
      return {
        x: e.touches[0].clientX - rect.left,
        y: e.touches[0].clientY - rect.top
      };
    } else {
      return {
        x: e.clientX - rect.left,
        y: e.clientY - rect.top
      };
    }
  };

  const startDrawing = (e) => {
    e.preventDefault();
    const coords = getCoordinates(e);
    if (!coords) return;
    
    const canvas = canvasRef.current;
    const ctx = canvas.getContext('2d');
    
    ctx.beginPath();
    ctx.moveTo(coords.x, coords.y);
    ctx.lineWidth = brushSize;
    ctx.lineCap = 'round';
    ctx.lineJoin = 'round';
    ctx.strokeStyle = '#ffffff'; // White ink for dark canvas
    
    setIsDrawing(true);
    
    if (autoPredictTimeoutRef.current) {
      clearTimeout(autoPredictTimeoutRef.current);
    }
  };

  const draw = (e) => {
    if (!isDrawing) return;
    e.preventDefault();
    
    const coords = getCoordinates(e);
    if (!coords) return;
    
    const canvas = canvasRef.current;
    const ctx = canvas.getContext('2d');
    
    ctx.lineTo(coords.x, coords.y);
    ctx.stroke();
  };

  const stopDrawing = () => {
    if (!isDrawing) return;
    setIsDrawing(false);
    
    // Save state in history
    saveState();
    
    // Trigger auto prediction if active
    if (autoPredict) {
      if (autoPredictTimeoutRef.current) {
        clearTimeout(autoPredictTimeoutRef.current);
      }
      autoPredictTimeoutRef.current = setTimeout(() => {
        handlePredict();
      }, 900); // Wait 900ms after drawing stops
    }
  };

  const saveState = () => {
    const canvas = canvasRef.current;
    if (canvas) {
      const state = canvas.toDataURL();
      const newHistory = history.slice(0, historyStep + 1);
      newHistory.push(state);
      setHistory(newHistory);
      setHistoryStep(newHistory.length - 1);
    }
  };

  const handleUndo = () => {
    if (historyStep > 0) {
      const newStep = historyStep - 1;
      setHistoryStep(newStep);
      
      const canvas = canvasRef.current;
      const ctx = canvas.getContext('2d');
      const img = new Image();
      img.src = history[newStep];
      img.onload = () => {
        ctx.drawImage(img, 0, 0);
        if (autoPredict) {
          handlePredict(history[newStep]);
        }
      };
    }
  };

  const handleClear = () => {
    const canvas = canvasRef.current;
    if (canvas) {
      const ctx = canvas.getContext('2d');
      ctx.fillStyle = '#0f172a';
      ctx.fillRect(0, 0, canvas.width, canvas.height);
      
      // Save clear state
      const state = canvas.toDataURL();
      const newHistory = history.slice(0, historyStep + 1);
      newHistory.push(state);
      setHistory(newHistory);
      setHistoryStep(newHistory.length - 1);
      
      if (autoPredictTimeoutRef.current) {
        clearTimeout(autoPredictTimeoutRef.current);
      }
    }
  };

  const handlePredict = (forcedImgData = null) => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    
    const imgData = forcedImgData || canvas.toDataURL();
    onPredict(imgData, 'canvas_drawing.png');
  };

  return (
    <div className="canvas-container card">
      <div className="card-header">
        <h3 className="card-title">Interactive Canvas Drawing</h3>
        <div className="flex gap-2 items-center">
          <label className="checkbox-label text-sm flex items-center gap-1.5 cursor-pointer">
            <input 
              type="checkbox" 
              checked={autoPredict} 
              onChange={(e) => setAutoPredict(e.target.checked)} 
              className="toggle-checkbox"
            />
            <span>Auto-Predict</span>
          </label>
        </div>
      </div>
      
      <div className="canvas-wrapper relative rounded-lg border border-slate-700 overflow-hidden bg-slate-900">
        <canvas
          ref={canvasRef}
          onMouseDown={startDrawing}
          onMouseMove={draw}
          onMouseUp={stopDrawing}
          onMouseLeave={stopDrawing}
          onTouchStart={startDrawing}
          onTouchMove={draw}
          onTouchEnd={stopDrawing}
          className="block w-full cursor-crosshair"
        />
        {isProcessing && (
          <div className="absolute inset-0 bg-slate-900/50 backdrop-blur-xs flex items-center justify-center pointer-events-none">
            <div className="loader">Analyzing stroke sequences...</div>
          </div>
        )}
      </div>
      
      <div className="canvas-controls mt-4 flex flex-wrap gap-4 items-center justify-between">
        <div className="flex items-center gap-2">
          <span className="text-sm font-medium text-slate-400">Brush Size:</span>
          <input
            type="range"
            min="4"
            max="24"
            value={brushSize}
            onChange={(e) => setBrushSize(parseInt(e.target.value))}
            className="slider"
          />
          <span className="text-sm font-mono text-slate-300 w-6">{brushSize}px</span>
        </div>
        
        <div className="flex gap-2">
          <button 
            onClick={handleUndo} 
            disabled={historyStep <= 0}
            className="btn btn-secondary"
            title="Undo last stroke"
          >
            Undo
          </button>
          <button 
            onClick={handleClear} 
            className="btn btn-danger"
            title="Clear canvas"
          >
            Clear
          </button>
          <button 
            onClick={() => handlePredict()} 
            disabled={isProcessing}
            className="btn btn-primary"
            title="Trigger prediction manually"
          >
            Analyze Drawing
          </button>
        </div>
      </div>
    </div>
  );
};

export default DrawingCanvas;
