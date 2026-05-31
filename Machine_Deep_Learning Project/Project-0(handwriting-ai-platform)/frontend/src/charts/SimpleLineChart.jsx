import React from 'react';

const SimpleLineChart = ({ 
  data = [], 
  valData = [], 
  labels = [], 
  title = "Metrics", 
  yLabel = "Value", 
  strokeColor = "#34d399", // Emerald-400
  valStrokeColor = "#60a5fa", // Blue-400
  height = 180 
}) => {
  if (data.length === 0) {
    return <div className="text-xs text-slate-500 text-center py-8">No data points.</div>;
  }

  const padding = 35;
  const chartHeight = height - padding * 2;
  
  // Find min and max for scaling
  const allValues = [...data, ...valData];
  const maxVal = Math.max(...allValues, 1.0);
  const minVal = Math.min(...allValues, 0.0);
  const valRange = maxVal - minVal || 1.0;

  // Calculate points coordinates
  const getPoints = (pointsData) => {
    return pointsData.map((val, idx) => {
      const xRatio = idx / (labels.length - 1 || 1);
      const yRatio = (val - minVal) / valRange;
      
      return {
        x: padding + xRatio * (320 - padding * 2), // Fixed SVG viewBox width 320
        y: padding + (1 - yRatio) * chartHeight
      };
    });
  };

  const trainPoints = getPoints(data);
  const valPoints = valData.length > 0 ? getPoints(valData) : [];

  // Generate SVG path string
  const getPathString = (pts) => {
    if (pts.length === 0) return "";
    return pts.reduce((acc, p, idx) => {
      return idx === 0 ? `M ${p.x} ${p.y}` : `${acc} L ${p.x} ${p.y}`;
    }, "");
  };

  const trainPath = getPathString(trainPoints);
  const valPath = getPathString(valPoints);

  // Generate Area SVG path string (for gradient fill under the training curve)
  const getAreaPathString = (pts) => {
    if (pts.length === 0) return "";
    const first = pts[0];
    const last = pts[pts.length - 1];
    const floorY = height - padding;
    return `${getPathString(pts)} L ${last.x} ${floorY} L ${first.x} ${floorY} Z`;
  };

  const trainAreaPath = getAreaPathString(trainPoints);

  // Grid lines (3 horizontal helper lines)
  const gridLines = [0, 0.5, 1].map((ratio) => {
    const yVal = minVal + ratio * valRange;
    const yCoord = padding + (1 - ratio) * chartHeight;
    return { y: yCoord, value: yVal.toFixed(2) };
  });

  return (
    <div className="simple-chart flex flex-col">
      <div className="flex justify-between items-center mb-1">
        <span className="text-[11px] font-semibold text-slate-400 uppercase tracking-wide">{title}</span>
        <div className="flex gap-2 text-[9px] font-medium">
          <div className="flex items-center gap-1 text-slate-350">
            <span className="w-1.5 h-1.5 rounded-full" style={{ backgroundColor: strokeColor }}></span>
            <span>Train</span>
          </div>
          {valData.length > 0 && (
            <div className="flex items-center gap-1 text-slate-350">
              <span className="w-1.5 h-1.5 rounded-full" style={{ backgroundColor: valStrokeColor }}></span>
              <span>Validation</span>
            </div>
          )}
        </div>
      </div>
      
      <div className="bg-slate-950/80 rounded border border-slate-850 p-1.5 relative overflow-hidden">
        <svg viewBox={`0 0 320 ${height}`} className="w-full h-auto overflow-visible">
          <defs>
            {/* Area gradient */}
            <linearGradient id={`area-grad-${title.replace(/\s+/g, '')}`} x1="0" y1="0" x2="0" y2="1">
              <stop offset="0%" stopColor={strokeColor} stopOpacity="0.15" />
              <stop offset="100%" stopColor={strokeColor} stopOpacity="0.00" />
            </linearGradient>
            
            {/* Drop shadow filter for line glow */}
            <filter id="glow" x="-20%" y="-20%" width="140%" height="140%">
              <feGaussianBlur stdDeviation="1.5" result="blur" />
              <feComposite in="SourceGraphic" in2="blur" operator="over" />
            </filter>
          </defs>

          {/* Grid lines */}
          {gridLines.map((line, idx) => (
            <g key={idx}>
              <line 
                x1={padding} 
                y1={line.y} 
                x2={320 - padding} 
                y2={line.y} 
                stroke="#1e293b" 
                strokeWidth="0.5" 
                strokeDasharray="2,2"
              />
              <text 
                x={padding - 5} 
                y={line.y + 3} 
                fill="#64748b" 
                fontSize="7" 
                textAnchor="end"
                fontFamily="monospace"
              >
                {line.value}
              </text>
            </g>
          ))}

          {/* X Axis Labels */}
          {labels.map((lbl, idx) => {
            const xRatio = idx / (labels.length - 1 || 1);
            const xCoord = padding + xRatio * (320 - padding * 2);
            return (
              <text 
                key={idx}
                x={xCoord} 
                y={height - padding + 12} 
                fill="#64748b" 
                fontSize="7" 
                textAnchor="middle"
                fontFamily="monospace"
              >
                {lbl}
              </text>
            );
          })}

          {/* Y Axis Label */}
          <text
            x={10}
            y={15}
            fill="#475569"
            fontSize="6"
            fontStyle="italic"
          >
            {yLabel}
          </text>

          {/* Training Area Gradient Fill */}
          {trainAreaPath && (
            <path 
              d={trainAreaPath} 
              fill={`url(#area-grad-${title.replace(/\s+/g, '')})`}
              className="fade-in"
            />
          )}

          {/* Validation Line */}
          {valPath && (
            <path 
              d={valPath} 
              fill="none" 
              stroke={valStrokeColor} 
              strokeWidth="1.2" 
              strokeLinecap="round"
            />
          )}

          {/* Training Line (Primary) */}
          {trainPath && (
            <path 
              d={trainPath} 
              fill="none" 
              stroke={strokeColor} 
              strokeWidth="1.5" 
              strokeLinecap="round"
              filter="url(#glow)"
            />
          )}

          {/* Data Points Markers */}
          {trainPoints.map((p, idx) => (
            <circle 
              key={`train-pt-${idx}`}
              cx={p.x} 
              cy={p.y} 
              r="2" 
              fill={strokeColor} 
              stroke="#0f172a" 
              strokeWidth="0.5" 
            />
          ))}
          
          {valPoints.map((p, idx) => (
            <circle 
              key={`val-pt-${idx}`}
              cx={p.x} 
              cy={p.y} 
              r="1.5" 
              fill={valStrokeColor} 
              stroke="#0f172a" 
              strokeWidth="0.5" 
            />
          ))}
        </svg>
      </div>
    </div>
  );
};

export default SimpleLineChart;
