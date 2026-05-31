import React, { useState } from 'react';

const ImageUploader = ({ onPredictFile, isProcessing }) => {
  const [dragActive, setDragActive] = useState(false);
  const [filesQueue, setFilesQueue] = useState([]);

  const handleDrag = (e) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === "dragenter" || e.type === "dragover") {
      setDragActive(true);
    } else if (e.type === "dragleave") {
      setDragActive(false);
    }
  };

  const processFiles = async (filesList) => {
    const validFiles = Array.from(filesList).filter(file => file.type.startsWith('image/'));
    
    if (validFiles.length === 0) {
      alert("Please upload valid image files (PNG, JPG, JPEG).");
      return;
    }

    // Map files to queue items
    const newQueueItems = validFiles.map(file => ({
      id: Math.random().toString(36).substring(2, 9),
      name: file.name,
      size: (file.size / 1024).toFixed(1) + ' KB',
      status: 'pending', // pending, processing, completed, error
      result: null,
      file: file
    }));

    setFilesQueue(prev => [...newQueueItems, ...prev]);

    // Process each file in the queue
    for (const item of newQueueItems) {
      setFilesQueue(prev => 
        prev.map(f => f.id === item.id ? { ...f, status: 'processing' } : f)
      );

      try {
        const base64 = await convertToBase64(item.file);
        const result = await onPredictFile(base64, item.name);
        
        setFilesQueue(prev => 
          prev.map(f => f.id === item.id ? { ...f, status: 'completed', result } : f)
        );
      } catch (err) {
        console.error(err);
        setFilesQueue(prev => 
          prev.map(f => f.id === item.id ? { ...f, status: 'error' } : f)
        );
      }
    }
  };

  const handleDrop = (e) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);
    
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      processFiles(e.dataTransfer.files);
    }
  };

  const handleFileInputChange = (e) => {
    if (e.target.files && e.target.files[0]) {
      processFiles(e.target.files);
    }
  };

  const convertToBase64 = (file) => {
    return new Promise((resolve, reject) => {
      const reader = new FileReader();
      reader.readAsDataURL(file);
      reader.onload = () => resolve(reader.result);
      reader.onerror = (error) => reject(error);
    });
  };

  const clearQueue = () => {
    setFilesQueue([]);
  };

  return (
    <div className="uploader-container card">
      <div className="card-header">
        <h3 className="card-title">Batch File Uploader</h3>
        {filesQueue.length > 0 && (
          <button onClick={clearQueue} className="btn btn-secondary text-xs py-1 px-2.5">
            Clear Queue
          </button>
        )}
      </div>

      <div 
        className={`dropzone rounded-lg border-2 border-dashed flex flex-col items-center justify-center p-8 text-center cursor-pointer transition-all duration-300 ${
          dragActive 
            ? 'border-emerald-500 bg-emerald-500/5' 
            : 'border-slate-700 bg-slate-900/50 hover:border-slate-600'
        }`}
        onDragEnter={handleDrag}
        onDragOver={handleDrag}
        onDragLeave={handleDrag}
        onDrop={handleDrop}
        onClick={() => document.getElementById('file-upload-input').click()}
      >
        <input 
          id="file-upload-input"
          type="file" 
          multiple 
          accept="image/*"
          className="hidden" 
          onChange={handleFileInputChange} 
        />
        <svg 
          className={`w-12 h-12 mb-3 transition-colors ${dragActive ? 'text-emerald-400' : 'text-slate-500'}`}
          fill="none" 
          stroke="currentColor" 
          viewBox="0 0 24 24"
        >
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="1.5" d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" />
        </svg>
        <p className="text-sm font-semibold text-slate-300">Drag & Drop images here</p>
        <p className="text-xs text-slate-500 mt-1">or click to browse from files</p>
        <p className="text-[10px] text-slate-600 mt-2">Supports JPG, PNG, JPEG</p>
      </div>

      {filesQueue.length > 0 && (
        <div className="files-list mt-4 max-h-[220px] overflow-y-auto pr-1">
          <div className="text-xs font-semibold text-slate-400 mb-2 uppercase tracking-wider">Queue:</div>
          <div className="flex flex-col gap-2">
            {filesQueue.map(item => (
              <div 
                key={item.id} 
                className="flex items-center justify-between p-2.5 rounded bg-slate-900 border border-slate-800 text-xs"
              >
                <div className="flex flex-col min-w-0 pr-2">
                  <span className="font-medium text-slate-300 truncate">{item.name}</span>
                  <span className="text-[10px] text-slate-500">{item.size}</span>
                </div>
                
                <div className="flex items-center gap-2 shrink-0">
                  {item.status === 'pending' && (
                    <span className="badge badge-warning">Queued</span>
                  )}
                  {item.status === 'processing' && (
                    <div className="flex items-center gap-1.5 text-sky-400 font-medium">
                      <span className="w-2 h-2 rounded-full bg-sky-400 animate-pulse"></span>
                      Analyzing...
                    </div>
                  )}
                  {item.status === 'completed' && (
                    <div className="flex items-center gap-1 text-emerald-400">
                      <span className="font-semibold">{item.result?.corrected_text || 'Empty'}</span>
                      <span className="text-[10px] text-slate-500">({(item.result?.avg_confidence * 100).toFixed(0)}%)</span>
                    </div>
                  )}
                  {item.status === 'error' && (
                    <span className="badge badge-danger">Failed</span>
                  )}
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};

export default ImageUploader;
