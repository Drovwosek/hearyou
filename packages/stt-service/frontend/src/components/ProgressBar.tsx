import React from 'react';
import { currentTimestamp } from '../utils/time';
import './ProgressBar.css';

interface ProgressBarProps {
  progress: number;
  visible: boolean;
  message?: string;
  showPercentage?: boolean;
  animated?: boolean;
  startTime?: number | null;
}

const ProgressBar: React.FC<ProgressBarProps> = ({
  progress,
  visible,
  message,
  showPercentage = true,
  animated = true,
  startTime,
}) => {
  const eta = (() => {
    if (!startTime || progress <= 0 || progress >= 100) {
      return '';
    }

    const elapsed = (currentTimestamp() - startTime) / 1000;
    const rate = progress / elapsed;
    const remaining = (100 - progress) / rate;

    if (!(remaining > 0) || !isFinite(remaining)) {
      return '';
    }

    if (remaining < 60) {
      return `~${Math.round(remaining)}с`;
    }

    if (remaining < 3600) {
      const minutes = Math.round(remaining / 60);
      return `~${minutes}м`;
    }

    const hours = Math.floor(remaining / 3600);
    const minutes = Math.round((remaining % 3600) / 60);
    return `~${hours}ч ${minutes}м`;
  })();

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
