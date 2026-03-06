import React from 'react';
import './ProgressBar.css';

interface ProgressBarProps {
  progress: number;
  visible: boolean;
}

const ProgressBar: React.FC<ProgressBarProps> = ({ progress, visible }) => {
  if (!visible) return null;

  return (
    <div className="progress-bar">
      <div className="progress-fill" style={{ width: `${progress}%` }} />
    </div>
  );
};

export default ProgressBar;
