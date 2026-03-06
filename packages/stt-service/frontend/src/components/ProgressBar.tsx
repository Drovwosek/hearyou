import React, { useState, useEffect } from 'react';
import './ProgressBar.css';

interface ProgressBarProps {
  progress: number;
  visible: boolean;
  message?: string;
  showPercentage?: boolean;
  animated?: boolean;
  startTime?: number;
}

const ProgressBar: React.FC<ProgressBarProps> = ({
  progress,
  visible,
  message,
  showPercentage = true,
  animated = true,
  startTime,
}) => {
  const [eta, setEta] = useState<string>('');

  useEffect(() => {
    if (!startTime || progress <= 0 || progress >= 100) {
      setEta('');
      return;
    }

    const elapsed = (Date.now() - startTime) / 1000; // seconds
    const rate = progress / elapsed; // % per second
    const remaining = (100 - progress) / rate; // seconds

    if (remaining > 0 && isFinite(remaining)) {
      if (remaining < 60) {
        setEta(`~${Math.round(remaining)}с`);
      } else if (remaining < 3600) {
        const minutes = Math.round(remaining / 60);
        setEta(`~${minutes}м`);
      } else {
        const hours = Math.floor(remaining / 3600);
        const minutes = Math.round((remaining % 3600) / 60);
        setEta(`~${hours}ч ${minutes}м`);
      }
    } else {
      setEta('');
    }
  }, [progress, startTime]);

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
          <div className="progress-stats">
            <div className="progress-percentage">
              {Math.round(progress)}%
            </div>
            {eta && (
              <div className="progress-eta">
                {eta}
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
};

export default ProgressBar;
