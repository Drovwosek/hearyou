import React from 'react';
import type { JTBDResult } from '../types';
import './JTBDAnalysis.css';

interface JTBDAnalysisProps {
  jtbd: JTBDResult;
}

const JTBDAnalysis: React.FC<JTBDAnalysisProps> = ({ jtbd }) => {
  return (
    <div className="jtbd-section">
      <div className="result-header">
        <h2>🎯 Анализ JTBD (Jobs-to-be-Done)</h2>
      </div>

      {jtbd.jobs && jtbd.jobs.length > 0 && (
        <div className="jtbd-category">
          <h3>💼 Jobs (Работы)</h3>
          <div className="jtbd-items">
            {jtbd.jobs.map((job, idx) => (
              <div key={idx} className="jtbd-card">
                <div className="jtbd-card-header">
                  <strong>{job.job}</strong>
                </div>
                <div className="jtbd-card-content">
                  <p>
                    <strong>Контекст:</strong> {job.context}
                  </p>
                  <p>
                    <strong>Результат:</strong> {job.outcome}
                  </p>
                  {job.quote && (
                    <blockquote className="jtbd-quote">"{job.quote}"</blockquote>
                  )}
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {jtbd.pains && jtbd.pains.length > 0 && (
        <div className="jtbd-category">
          <h3>😰 Pains (Боли)</h3>
          <div className="jtbd-items">
            {jtbd.pains.map((pain, idx) => (
              <div key={idx} className="jtbd-card pain">
                <div className="jtbd-card-header">
                  <strong>{pain.pain}</strong>
                  <span className="severity">{pain.severity}</span>
                </div>
                <div className="jtbd-card-content">
                  <p>
                    <strong>Контекст:</strong> {pain.context}
                  </p>
                  {pain.quote && (
                    <blockquote className="jtbd-quote">"{pain.quote}"</blockquote>
                  )}
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {jtbd.gains && jtbd.gains.length > 0 && (
        <div className="jtbd-category">
          <h3>✨ Gains (Выгоды)</h3>
          <div className="jtbd-items">
            {jtbd.gains.map((gain, idx) => (
              <div key={idx} className="jtbd-card gain">
                <div className="jtbd-card-header">
                  <strong>{gain.gain}</strong>
                  <span className="value">{gain.value}</span>
                </div>
                <div className="jtbd-card-content">
                  <p>
                    <strong>Контекст:</strong> {gain.context}
                  </p>
                  {gain.quote && (
                    <blockquote className="jtbd-quote">"{gain.quote}"</blockquote>
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

export default JTBDAnalysis;
