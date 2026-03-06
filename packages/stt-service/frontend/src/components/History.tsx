import React, { useState } from 'react';
import HistoryItem from './HistoryItem';
import { useHistory } from '../hooks/useHistory';
import type { TranscriptionResult } from '../types';
import './History.css';

interface HistoryProps {
  onLoad: (result: TranscriptionResult) => void;
}

const History: React.FC<HistoryProps> = ({ onLoad }) => {
  const { history, loading, error, fetchHistory, loadTranscription } = useHistory();
  const [isExpanded, setIsExpanded] = useState(false);
  const [loadingTaskId, setLoadingTaskId] = useState<string | null>(null);

  const handleItemClick = async (item: any) => {
    if (item.status !== 'completed') {
      alert('Эта транскрипция ещё не завершена');
      return;
    }

    setLoadingTaskId(item.task_id);
    
    try {
      const result = await loadTranscription(item.task_id);
      onLoad(result);
      
      // Scroll to result after a brief delay
      setTimeout(() => {
        document.querySelector('.result-section')?.scrollIntoView({ 
          behavior: 'smooth', 
          block: 'start' 
        });
      }, 100);
    } catch (err) {
      alert(`Не удалось загрузить результат: ${err instanceof Error ? err.message : 'Unknown error'}`);
    } finally {
      setLoadingTaskId(null);
    }
  };

  if (history.length === 0 && !loading) {
    return null;
  }

  return (
    <div className="history-section">
      <div className="history-header" onClick={() => setIsExpanded(!isExpanded)}>
        <h2>
          <span className="history-icon">📜</span>
          История транскрибаций
          {history.length > 0 && (
            <span className="history-badge">{history.length}</span>
          )}
        </h2>
        <button className="history-toggle" aria-label="Toggle history">
          {isExpanded ? '▼' : '▶'}
        </button>
      </div>

      {isExpanded && (
        <div className="history-content">
          {loading && history.length === 0 ? (
            <div className="history-loading">
              <div className="spinner"></div>
              <span>Загрузка истории...</span>
            </div>
          ) : error ? (
            <div className="history-error">
              <span className="error-icon">⚠️</span>
              <span>{error}</span>
              <button onClick={fetchHistory} className="retry-button">
                Повторить
              </button>
            </div>
          ) : history.length === 0 ? (
            <div className="history-empty">
              <span className="empty-icon">📭</span>
              <p>История пуста</p>
            </div>
          ) : (
            <div className="history-list">
              {history.map((item) => (
                <div key={item.task_id} className="history-item-wrapper">
                  <HistoryItem item={item} onClick={handleItemClick} />
                  {loadingTaskId === item.task_id && (
                    <div className="loading-overlay">
                      <div className="spinner-small"></div>
                    </div>
                  )}
                </div>
              ))}
            </div>
          )}
          
          {!loading && !error && history.length > 0 && (
            <div className="history-footer">
              <button onClick={fetchHistory} className="refresh-button" disabled={loading}>
                🔄 Обновить
              </button>
            </div>
          )}
        </div>
      )}
    </div>
  );
};

export default History;
