import React from 'react';
import './ProgressBar.css';

interface ProgressBarProps {
  progress: number;
  visible: boolean;
  message?: string;
  showPercentage?: boolean;
  animated?: boolean;
}

const ProgressBar: React.FC<ProgressBarProps> = ({
  progress,
  visible,
  message,
  showPercentage = true,
  animated = true,
}) => {
  if (!visible) return null;

  return (
    <div className="progress-bar-container">
      {message && <div className="progress-message">{message}</div>}
      
      <div className="progress-bar-wrapper">
        <div className="progress-bar">
          <div
            className={`progress-fill ${animated ? 'animated' : ''}`}
            style={{ width: `${Math.min(100, Math.max(0, progress))}%` }}
          >
            {animated && <div className="progress-shimmer" />}
          </div>
        </div>
        
        {showPercentage && (
          <div className="progress-percentage">
            {Math.round(progress)}%
          </div>
        )}
      </div>
    </div>
  );
};

export default ProgressBar;
