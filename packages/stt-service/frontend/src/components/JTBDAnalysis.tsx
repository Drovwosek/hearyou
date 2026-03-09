import React, { useState } from 'react';
import JTBDCategory from './JTBDCategory';
import { useJTBD } from '../hooks/useJTBD';
import type { JTBDResult } from '../types';
import './JTBDAnalysis.css';

interface JTBDAnalysisProps {
  jtbd: JTBDResult;
}

const JTBDAnalysis: React.FC<JTBDAnalysisProps> = ({ jtbd }) => {
  const [isExpanded, setIsExpanded] = useState(true);
  const { categories, totalElements, hasData } = useJTBD(jtbd);

  if (!hasData) {
    return (
      <div className="jtbd-section">
        <div className="jtbd-header">
          <h2>
            <span className="jtbd-icon">🎯</span>
            Анализ JTBD
          </h2>
        </div>
        <div className="jtbd-empty">
          <span className="empty-icon">📊</span>
          <p>Нет данных для анализа</p>
        </div>
      </div>
    );
  }

  return (
    <div className="jtbd-section">
      <div className="jtbd-header" onClick={() => setIsExpanded(!isExpanded)}>
        <h2>
          <span className="jtbd-icon">🎯</span>
          Анализ JTBD (Jobs-to-be-Done)
          <span className="jtbd-badge">{totalElements}</span>
        </h2>
        <button className="jtbd-toggle" aria-label="Toggle JTBD analysis">
          {isExpanded ? '▼' : '▶'}
        </button>
      </div>

      {isExpanded && (
        <div className="jtbd-content">
          <div className="jtbd-description">
            <p>
              <strong>Jobs-to-be-Done</strong> — фреймворк для понимания истинных потребностей 
              пользователей через анализ их целей (jobs), болей (pains) и выгод (gains).
            </p>
          </div>

          <div className="jtbd-categories">
            {categories.map((category, idx) => (
              <JTBDCategory key={idx} category={category} />
            ))}
          </div>
        </div>
      )}
    </div>
  );
};

export default JTBDAnalysis;
