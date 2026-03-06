import React from 'react';
import type { HistoryItem } from '../types';
import './History.css';

interface HistoryProps {
  items: HistoryItem[];
  onLoad: (item: HistoryItem) => void;
  onClear: () => void;
}

const History: React.FC<HistoryProps> = ({ items, onLoad, onClear }) => {
  if (items.length === 0) return null;

  const formatDate = (timestamp: number): string => {
    const date = new Date(timestamp);
    const now = new Date();
    const diffMs = now.getTime() - date.getTime();
    const diffMins = Math.floor(diffMs / 60000);
    const diffHours = Math.floor(diffMs / 3600000);
    const diffDays = Math.floor(diffMs / 86400000);

    if (diffMins < 60) return `${diffMins} мин назад`;
    if (diffHours < 24) return `${diffHours} ч назад`;
    if (diffDays < 7) return `${diffDays} дн назад`;

    return date.toLocaleDateString('ru-RU', {
      day: 'numeric',
      month: 'short',
      hour: '2-digit',
      minute: '2-digit',
    });
  };

  return (
    <div className="history-section">
      <div className="history-header">
        <h2>📜 История транскрибаций</h2>
        <button className="clear-history-btn" onClick={onClear}>
          🗑️ Очистить
        </button>
      </div>

      <div className="history-list">
        {items.map((item) => (
          <div
            key={item.task_id}
            className="history-item"
            onClick={() => onLoad(item)}
          >
            <div className="history-item-content">
              <div className="history-filename">📄 {item.filename}</div>
              <div className="history-meta">
                <span className="history-time">🕐 {formatDate(item.timestamp)}</span>
                {item.speaker_labeling && <span className="history-badge">🎭</span>}
                {item.jtbd_analysis && <span className="history-badge">🎯</span>}
              </div>
            </div>
            <div className="history-arrow">→</div>
          </div>
        ))}
      </div>
    </div>
  );
};

export default History;
