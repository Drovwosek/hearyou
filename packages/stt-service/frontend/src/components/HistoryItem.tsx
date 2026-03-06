import React from 'react';
import type { HistoryEntry } from '../hooks/useHistory';
import './HistoryItem.css';

interface HistoryItemProps {
  item: HistoryEntry;
  onClick: (item: HistoryEntry) => void;
}

const HistoryItem: React.FC<HistoryItemProps> = ({ item, onClick }) => {
  const formatDate = (timestamp: string): string => {
    try {
      const date = new Date(timestamp);
      const now = new Date();
      const diffMs = now.getTime() - date.getTime();
      const diffMins = Math.floor(diffMs / 60000);
      const diffHours = Math.floor(diffMs / 3600000);
      const diffDays = Math.floor(diffMs / 86400000);

      if (diffMins < 1) return 'только что';
      if (diffMins < 60) return `${diffMins} мин назад`;
      if (diffHours < 24) return `${diffHours} ч назад`;
      if (diffDays < 7) return `${diffDays} дн назад`;

      return date.toLocaleDateString('ru-RU', {
        day: 'numeric',
        month: 'short',
        hour: '2-digit',
        minute: '2-digit',
      });
    } catch {
      return timestamp;
    }
  };

  const getStatusIcon = (status: string): string => {
    switch (status) {
      case 'completed':
        return '✅';
      case 'processing':
        return '⏳';
      case 'failed':
        return '❌';
      default:
        return '📄';
    }
  };

  return (
    <div className="history-item" onClick={() => onClick(item)}>
      <div className="history-item-icon">{getStatusIcon(item.status)}</div>
      <div className="history-item-content">
        <div className="history-item-filename">{item.filename}</div>
        <div className="history-item-meta">
          <span className="history-item-time">🕐 {formatDate(item.created_at)}</span>
          {item.user && item.user !== 'anonymous' && (
            <span className="history-item-user">👤 {item.user}</span>
          )}
        </div>
      </div>
      <div className="history-item-arrow">→</div>
    </div>
  );
};

export default HistoryItem;
